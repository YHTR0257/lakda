import { renderHook, act } from "@testing-library/react";
import { useChatAsk } from "./useChatAsk";
import { useAskStore } from "@/store/askStore";

jest.mock("@/app/ask/actions", () => ({
  confirmQuestion: jest.fn(),
}));

jest.mock("react", () => ({
  ...jest.requireActual("react"),
  useTransition: jest.fn(() => [false, (fn: () => void) => fn()]),
}));

const { confirmQuestion } = jest.requireMock("@/app/ask/actions");

describe("useChatAsk", () => {
  beforeEach(() => {
    useAskStore.getState().clearMessages();
    jest.clearAllMocks();
  });

  it("初期状態でメッセージが空であること", () => {
    const { result } = renderHook(() => useChatAsk());
    expect(result.current.messages).toHaveLength(0);
    expect(result.current.isPending).toBe(false);
  });

  it("inputRef と submit と clearMessages を返すこと", () => {
    const { result } = renderHook(() => useChatAsk());
    expect(result.current.inputRef).toBeDefined();
    expect(typeof result.current.submit).toBe("function");
    expect(typeof result.current.clearMessages).toBe("function");
  });

  it("submit を呼ぶとユーザーメッセージが追加されること", async () => {
    confirmQuestion.mockResolvedValue({
      success: true,
      answer: {
        session_id: "s1",
        question: "テスト質問",
        answer: "テスト回答",
        sources: [],
        timestamp: "2026-01-01T00:00:00Z",
      },
      answerHtml: "<p>テスト回答</p>",
      error: "",
    });

    const { result } = renderHook(() => useChatAsk());

    await act(async () => {
      result.current.submit("テスト質問");
    });

    const messages = result.current.messages;
    expect(messages.length).toBeGreaterThanOrEqual(1);
    expect(messages[0].role).toBe("user");
    expect(messages[0].text).toBe("テスト質問");
  });

  it("空文字では submit しないこと", async () => {
    const { result } = renderHook(() => useChatAsk());

    await act(async () => {
      result.current.submit("   ");
    });

    expect(result.current.messages).toHaveLength(0);
    expect(confirmQuestion).not.toHaveBeenCalled();
  });

  it("clearMessages を呼ぶとメッセージがクリアされること", async () => {
    confirmQuestion.mockResolvedValue({
      success: true,
      answer: {
        session_id: "s1",
        question: "テスト",
        answer: "回答",
        sources: [],
        timestamp: "2026-01-01T00:00:00Z",
      },
      answerHtml: null,
      error: "",
    });

    const { result } = renderHook(() => useChatAsk());

    await act(async () => {
      result.current.submit("テスト質問です");
    });

    act(() => {
      result.current.clearMessages();
    });

    expect(result.current.messages).toHaveLength(0);
  });
});
