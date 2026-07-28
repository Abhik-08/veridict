import { api } from "./api";

export interface EvaluationRequest {
  question: string;
  aiResponse: string;
  referenceAnswer?: string;
  file?: File | null;
}

export const evaluateResponse = async ({
  question,
  aiResponse,
  referenceAnswer,
  file,
}: EvaluationRequest) => {
  const formData = new FormData();

  formData.append("question", question);
  formData.append("ai_response", aiResponse);

  if (referenceAnswer) {
    formData.append("reference_answer", referenceAnswer);
  }

  if (file) {
    formData.append("pdf_file", file);
  }

  const response = await api.post("/evaluate", formData);

  return response.data;
};

export const exportEvaluationPDF = async (resultData: any) => {
  const response = await api.post("/evaluate/export-pdf", resultData, {
    headers: {
      "Content-Type": "application/json",
    },
    responseType: "blob",
  });

  const blob = new Blob([response.data], { type: "application/pdf" });
  const url = window.URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  const nowStr = new Date().toISOString().slice(0, 10);
  link.download = `Veridict-Evaluation-Report-${nowStr}.pdf`;
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};