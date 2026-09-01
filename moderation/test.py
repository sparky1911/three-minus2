import grpc
import moderation_pb2 as pb
import moderation_pb2_grpc as pb_grpc

with grpc.insecure_channel("localhost:50051") as ch:
    stub = pb_grpc.ModerationStub(ch)
    r = stub.Moderate(pb.ModerateRequest(comment_id="test-1", text="hello", author_id="u1"))
    print(r)