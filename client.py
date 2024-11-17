import grpc
import financial_service_pb2 as pb2
import financial_service_pb2_grpc as pb2_grpc

def run_tests():
    # Connessione al server gRPC
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = pb2_grpc.FinancialServiceStub(channel)

        # Test: Registrazione di un utente
        print("\n=== RegisterUser Test ===")
        register_request = pb2.UserRequest(email="test_user@example.com", ticker="AAPL")
        register_response = stub.RegisterUser(register_request)
        print(f"Response: {register_response.message} (success: {register_response.success})")

        # Test: Aggiornamento di un utente
        print("\n=== UpdateUser Test ===")
        update_request = pb2.UserRequest(email="test_user@example.com", ticker="MSFT")
        update_response = stub.UpdateUser(update_request)
        print(f"Response: {update_response.message} (success: {update_response.success})")

        # Test: Cancellazione di un utente
        print("\n=== DeleteUser Test ===")
        delete_request = pb2.UserRequest(email="test_user@example.com")
        delete_response = stub.DeleteUser(delete_request)
        print(f"Response: {delete_response.message} (success: {delete_response.success})")

        # Test: Recupero dell'ultimo valore disponibile
        print("\n=== GetLatestValue Test ===")
        latest_value_request = pb2.UserRequest(email="test_user@example.com")
        latest_value_response = stub.GetLatestValue(latest_value_request)
        print(f"Value: {latest_value_response.value} (timestamp: {latest_value_response.timestamp}, success: {latest_value_response.success})")

        # Test: Calcolo della media degli ultimi X valori
        print("\n=== GetAverageValue Test ===")
        average_request = pb2.StockHistoryRequest(email="test_user@example.com", count=5)
        average_response = stub.GetAverageValue(average_request)
        print(f"Average Value: {average_response.value} (timestamp: {average_response.timestamp}, success: {average_response.success})")

if __name__ == "__main__":
    run_tests()
