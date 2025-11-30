"""
The code to related to the database management will be done here
All the POST requests will be handled from db_management instance
"""

from collections import deque
from datetime import datetime
import config as cfg
import asyncio
import time
from utils._chunking import naive_sentence_chunking, naive_word_chunking, semantic_chunking
from utils._text_extraction import naive_text_extraction 
from utils._execute_job import execute

class _JobManagement():
    def __init__(self, db, model, logger, queue=deque(maxlen=cfg.max_queue_length)):
        self.queue = queue
        self.db_es = db
        self.status = "idle" # idle or busy
        self.current_job = {}
        self.jobs_history = {"success": [], "failed": []}
        self.model = model
        self.naive_text_extraction = naive_text_extraction(logger)
        self.naive_sentence_chunking = naive_sentence_chunking(logger)
        self.naive_word_chunking = naive_word_chunking()
        self.semantic_chunking = semantic_chunking(logger=logger)
        self.execute = execute(
            db, 
            model, 
            logger,
            self.naive_text_extraction, 
            self.naive_sentence_chunking, 
            self.naive_word_chunking, 
            self.semantic_chunking
        )
        self.logger = logger
        

    async def start_jobs(self):
        """
        while queue is not empty
            1. Pop the job from the queue
            2. Change the job status
            3. Start and finish the job
            4. Change the job status
            5. Record the job history
        """


        while self.queue:
            self.current_job = self.queue.popleft()

            # result = self.start_job() # if use `job_manager.handle_jobs()` from main_backend.py file
            # if use `asyncio.create_task(job_manager.handle_jobs())` from main_backend.py file
            # self.record_job_history(result)
            # print(f"Start Job: {self.current_job}")
            # self.start_job()
            
            result = await asyncio.to_thread(self.start_job) 
            self.current_job = {}
            time.sleep(1)

        self.status = "idle"


    def record_job_history(self, result):
        """
        1. Record the job history
        2. Return the result
        """
        # refine self.current_job
        if result:
            self.jobs_history["Success"].append(job)
        else:
            self.jobs_history["Failed"].append(job)
        return result


    def add_new_jobs(self, jobs):
        for job in jobs:
            self.queue.append(job)


    def start_job(self):
        
        try:
            info = self.current_job["settings"]
            text_file = self.current_job["text_file"]
            target_index_type = info["target_index_type"]
            if target_index_type == "full_text":
                _title = info["properties"]["title"]
            else:
                _title = info["properties"]["original_full_text_data_title"]
            
            self.logger.info(f"start_job() - file title: {_title}")
        except Exception as e:
            self.logger.exception(f"Error retrieving job info from start_job(): {str(e)}")

        try:            
            result = self.execute.start(info, target_index_type, text_file)

            # if target_index_type == "full_text":
            #     result = self.execute.add_full_text(info, text_file)
            # elif target_index_type == "full_vector":
            #     result = self.execute.add_full_vector(info)
            # elif target_index_type == "chunked_pairs":
            #     result = self.execute.add_chunked_pairs(info)

            self.logger.info(f"start_job() - Jobs done with adding {_title} to {target_index_type} index type")

        except Exception as e:
            self.logger.exception(f"Error in job manager start_job(): {str(e)}")
            result = {"status": False, "message": str(e)}

        return result


    
    async def get_status_summary(self):
        """
        queue length
        current job type
        current job step        
        """
        _title = None
        _type = None
        _step = None
        if self.current_job:
            if self.current_job["settings"]["target_index_type"] == "full_text":
                _title = self.current_job["settings"]["properties"]["title"]
            else:
                _title = self.current_job["settings"]["properties"]["original_full_text_data_title"]
            _type = self.current_job["settings"]["target_index_type"]
            _step = self.execute.current_step

        summary = {
            "Current Job info": {
                "Title": _title,
                "Type": _type,
                "Step": _step
                # "Title": self.execute
                # "Type": self.current_job["settings"]["target_index_type"] if self.current_job else None,
                # "Step": self.execute.current_step if self.current_job else None
            },
            "Queue info": {
                "Length": len(self.queue),

            },
        }
        return summary
    

