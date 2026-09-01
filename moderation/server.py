from concurrent import futures
import grpc

import moderation_pb2 as pb
import moderation_pb2_grpc as pb_grpc
from wordlist import check
from classifier import toxicity_score
from llm import llm_check

REJECT_AT = 0.80
APPROVE_UNDER = 0.25


class ModerationServicer(pb_grpc.ModerationServicer):
    def Moderate(self, request, context):
        text = request.text
        cid = request.comment_id

        # stage 1 — wordlist
        result, terms = check(text)
        if result == "BLOCK":
            return pb.Verdict(comment_id=cid, decision=pb.REJECT,
                              score=1.0, stage="wordlist")

        # stage 2 — classifier
        score = toxicity_score(text)
        if result == "FLAG":
            score = max(score, 0.4)

        if score >= REJECT_AT:
            return pb.Verdict(comment_id=cid, decision=pb.REJECT,
                              score=score, stage="classifier")

        if score < APPROVE_UNDER:
            return pb.Verdict(comment_id=cid, decision=pb.APPROVE,
                              score=score, stage="classifier")

        # stage 3 — LLM (uncertain band only)
        try:
            verdict, _ = llm_check(text)
            decision = pb.REJECT if verdict == "REJECT" else pb.APPROVE
        except Exception as e:
            print(f"llm stage failed for {cid}: {e}")
            decision = pb.REVIEW

        return pb.Verdict(comment_id=cid, decision=decision,
                          score=score, stage="llm")
def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=4))
    pb_grpc.add_ModerationServicer_to_server(ModerationServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("listening on :50051")
    server.wait_for_termination()


if __name__ == "__main__":
    serve()