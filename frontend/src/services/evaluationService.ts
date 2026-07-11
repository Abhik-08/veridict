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