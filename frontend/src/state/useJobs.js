import { useEffect, useRef, useState, useCallback } from "react";
import { getStatus } from "../api/ocr.api";
import { JOB_STATUS, normalizeStatus } from "../constants/jobStatus";

const TERMINAL_JOB_STATUSES = [JOB_STATUS.COMPLETED, JOB_STATUS.FAILED];

export function useJobs(pollInterval = 2000) {
  const [jobs, setJobs] = useState([]);
  const jobsRef = useRef(jobs);
  const pollRef = useRef(null);

  useEffect(() => {
    jobsRef.current = jobs;
  }, [jobs]);

  const pollOnce = useCallback(async () => {
    const currentJobs = jobsRef.current;

    const results = await Promise.all(
      currentJobs.map(async (job) => {
        if (TERMINAL_JOB_STATUSES.includes(normalizeStatus(job.status))) {
          return job;
        }

        const status = await getStatus(job.id);

        if (!status) return job;

        return { ...job, ...status };
      })
    );

    // Drop jobs that just reached a terminal state
    const stillActive = results.filter(
      (job) => !TERMINAL_JOB_STATUSES.includes(normalizeStatus(job.status))
    );

    setJobs(stillActive);
  }, []);

  useEffect(() => {
    const hasActiveJobs = jobs.some(
      (job) => !TERMINAL_JOB_STATUSES.includes(normalizeStatus(job.status))
    );

    if (hasActiveJobs && !pollRef.current) {
      pollRef.current = setInterval(pollOnce, pollInterval);
    }

    if (!hasActiveJobs && pollRef.current) {
      clearInterval(pollRef.current);
      pollRef.current = null;
    }

    return () => {
      if (pollRef.current) {
        clearInterval(pollRef.current);
        pollRef.current = null;
      }
    };
  }, [jobs, pollInterval, pollOnce]);

  function addJob(job) {
    setJobs((prev) => [job, ...prev]);
  }

  function clearJobs() {
    setJobs([]);
  }

  return { jobs, addJob, clearJobs };
}