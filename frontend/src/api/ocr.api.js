import { api, safe } from "./client";

export async function uploadFile(file) {
  const form = new FormData();
  form.append("file", file);

  const res = await safe(() =>
    api.post("/api/v1/documents", form, {
      headers: { "Content-Type": "multipart/form-data" },
    })
  );

  if (!res?.data) return null;

  const data = res.data;

  return {
    id: data.id,
    status: data.status || "PENDING",
    ...data,
  };
}

export async function getStatus(documentId) {
  const res = await safe(() =>
    api.get(`/api/v1/documents/${documentId}/status`)
  );
  return res?.data || null;
}

export async function getResult(documentId) {
  const res = await safe(() =>
    api.get(`/api/v1/documents/${documentId}/url`)
  );
  return res?.data || null;
}