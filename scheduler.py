# scheduler.py
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import logging
import sqlite3

class ScheduleManager:
    def __init__(self, db):
        self.scheduler = BackgroundScheduler()
        self.db = db
        logging.basicConfig()
        logging.getLogger('apscheduler').setLevel(logging.DEBUG)

    def start(self):
        """Start the background scheduler"""
        self.scheduler.start()
        
    def schedule_task(self, task_id, delay, description):
        """
        Schedule a task to be executed after the specified delay
        
        Args:
            task_id (int): The database ID of the task
            delay (int): Delay in seconds before task execution
            description (str): Task description
        """
        run_time = datetime.now() + timedelta(seconds=delay)
        
        # Schedule the main task execution
        self.scheduler.add_job(
            self.execute_task,
            'date',
            run_date=run_time,
            args=[task_id, description],
            id=f'task_{task_id}'
        )
        
        # Schedule notification 5 minutes before execution
        notify_time = run_time - timedelta(minutes=5)
        if notify_time > datetime.now():
            self.scheduler.add_job(
                self.notify_user,
                'date',
                run_date=notify_time,
                args=[task_id, description],
                id=f'notify_{task_id}'
            )

    def execute_task(self, task_id, description):
        """
        Execute the scheduled task
        
        Args:
            task_id (int): The database ID of the task
            description (str): Task description
        """
        try:
            # Update task status in database
            with sqlite3.connect(self.db.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE tasks SET status = ? WHERE id = ?',
                    ('completed', task_id)
                )
                conn.commit()
                
            # Log successful execution
            logging.info(f"Task {task_id} completed: {description}")
            
            # Remove the job from scheduler
            self.scheduler.remove_job(f'task_{task_id}')
            
        except Exception as e:
            logging.error(f"Error executing task {task_id}: {e}")

    def notify_user(self, task_id, description):
        """
        Send notification for upcoming task
        
        Args:
            task_id (int): The database ID of the task
            description (str): Task description
        """
        try:
            # Get task status
            with sqlite3.connect(self.db.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT status FROM tasks WHERE id = ?', (task_id,))
                result = cursor.fetchone()
                
                # Only notify if task is still pending
                if result and result[0] == 'pending':
                    logging.info(f"Notification sent for task {task_id}: {description}")
                    # Note: Actual notification logic would go here when integrated with bot messaging
                
            # Remove the notification job
            self.scheduler.remove_job(f'notify_{task_id}')
            
        except Exception as e:
            logging.error(f"Error notifying for task {task_id}: {e}")

    def cancel_task(self, task_id):
        """
        Cancel a scheduled task
        
        Args:
            task_id (int): The database ID of the task to cancel
        """
        try:
            # Remove main task job
            try:
                self.scheduler.remove_job(f'task_{task_id}')
            except:
                pass
                
            # Remove notification job
            try:
                self.scheduler.remove_job(f'notify_{task_id}')
            except:
                pass
                
            # Update task status in database
            with sqlite3.connect(self.db.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    'UPDATE tasks SET status = ? WHERE id = ?',
                    ('cancelled', task_id)
                )
                conn.commit()
                
            logging.info(f"Task {task_id} cancelled successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error cancelling task {task_id}: {e}")
            return False

    def reschedule_task(self, task_id, new_delay):
        """
        Reschedule an existing task
        
        Args:
            task_id (int): The database ID of the task
            new_delay (int): New delay in seconds
        """
        try:
            # Get task description
            with sqlite3.connect(self.db.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT description FROM tasks WHERE id = ?', (task_id,))
                result = cursor.fetchone()
                
                if not result:
                    raise ValueError(f"Task {task_id} not found")
                    
                description = result[0]
            
            # Cancel existing schedule
            self.cancel_task(task_id)
            
            # Create new schedule
            self.schedule_task(task_id, new_delay, description)
            
            logging.info(f"Task {task_id} rescheduled successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error rescheduling task {task_id}: {e}")
            return False

    def stop(self):
        """Shutdown the scheduler"""
        self.scheduler.shutdown()