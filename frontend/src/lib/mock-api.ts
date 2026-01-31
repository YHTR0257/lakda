import { ApiException } from "@/lib/api";
import type { Interpretation, Answer } from "@/types/ask";

const mockInterpretations: Record<string, Interpretation> = {};
const mockAnswers: Record<string, Answer> = {};

// モックAPI: 質問の解釈を取得
function generateId(): string {
  return Math.random().toString(36).substring(2, 10);
}

function delay(ms: number = 1000): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function mockSubmitQuestion(question: string) {
  await delay(1000);

  // Error pattern 1: Too short question
  if (question.trim().length < 10) {
    throw new ApiException(
      400,
      "Question is too short",
      "QUESTION_VALIDATION_ERROR",
      {
        minLength: 10,
        actualLength: question.trim().length,
      }
    );
  }

  const interpretationId = generateId();
  const interpretation: Interpretation = {
    id: interpretationId,
    questionId: generateId(),
    originalQuestion: question,
    interpretedQuery: `${question}に関する先行事例を探索する。先行事例をMECEに分解してそれらの特徴を説明`,
    keywords: ["先行事例", "MECE", "特徴"],
    intent: "先行事例調査",
    timestamp: new Date().toISOString(),
    confidenceScore: 0.95,
  };
  mockInterpretations[interpretationId] = interpretation;

  return { success: true, interpretationId };
}

export async function mockGetInterpretation(
  id: string
): Promise<Interpretation> {
  await delay(500);

  // Error pattern 1: Not exist interpretationId
  if (!mockInterpretations[id]) {
    throw new ApiException(
      404,
      "Interpretation not found",
      "INTERPRETATION_NOT_FOUND",
      { interpretationId: id }
    );
  }

  const interpretation = mockInterpretations[id];
  if (interpretation.confidenceScore < 0.3) {
    throw new ApiException(
      422,
      "Low confidence in interpretation",
      "LOW_CONFIDENCE",
      { confidenceScore: interpretation.confidenceScore }
    );
  }

  return interpretation;
}

export async function mockConfirmInterpretation(
  interpretationId: string,
  interpretedQuery: string,
  keywords: string[],
  intent: string
) {
  await delay(500);

  // TODO: Implement Error pattern 1: Not pass validation

  const answerId = generateId();
  const answer: Answer = {
    id: answerId,
    interpretationId,
    answerText: `
# Overview
- 先行事例として、事例AA、事例BB、事例CCが存在します。
- これらの事例はMECEに分類され、それぞれの特徴は以下の通りです。

# Question
${mockInterpretations[interpretationId].originalQuestion}
解釈「${interpretedQuery}」に基づく回答です。\nキーワード: ${keywords.join(", ")}、意図: ${intent}。

# Answer

## 先行事例のMECE分類と特徴
1. 事例AA
   - 特徴: 高い信頼性とスケーラビリティを持つ。
2. 事例BB
   - 特徴: コスト効率が良く、導入が容易。
3. 事例CC
   - 特徴: 柔軟なカスタマイズが可能で、多様なニーズに対応。

以上が、質問に対する回答です。`,
    sources: [
      {
        documentId: "doc-1234",
        title: "ドキュメントA",
        excerpt: "ドキュメントAの抜粋...",
        relevanceScore: 0.95,
      },
      {
        documentId: "doc-5678",
        title: "ドキュメントB",
        excerpt: "ドキュメントBの抜粋...",
        relevanceScore: 0.9,
      },
    ],
    timestamp: new Date().toISOString(),
    confidenceScore: 0.9,
  };
  mockAnswers[answerId] = answer;

  return { success: true, answerId };
}

export async function mockGetAnswer(id: string) {
  await delay(500);

  const answer = mockAnswers[id];
  if (!answer) {
    return { success: false, error: "回答が見つかりません。" };
  }

  return { success: true, answer };
}
