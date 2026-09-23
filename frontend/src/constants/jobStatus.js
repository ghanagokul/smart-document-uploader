/**
 * Canonical OCR job lifecycle states.
 *
 * These values MUST exactly match backend responses
 * (see DocumentStatus enum in app/models/document.py).
 * Do not rename without backend coordination.
 */
// src/constants/jobStatus.js
export const JOB_STATUS = Object.freeze({
  PENDING: "pending",
  COMPLETED: "completed",
  FAILED: "failed",
});

export function normalizeStatus(status) {
  return (status || "").toLowerCase();
}