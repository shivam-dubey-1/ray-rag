1. deploy qdrant vector db

helm repo add qdrant https://qdrant.to/helm

helm install qdrant qdrant/qdrant 

2. create a docker image withy attahce docker file or use the image in job.yaml


3. Deploy job.yaml

4. After job ran successfully you can  test if the data got loaded into vector db

   port forward kubectl port-forward svc/qdrant 6333:6333 and riun this on other tab

curl -X POST http://localhost:6333/collections/knowledge_base/points/scroll -H 'Content-Type: application/json' -d '{"limit": 10, "with_payload": true, "with_vector": false}'

{"result":{"points":[{"id":298834018309226939,"payload":{"text":"Quantum computing uses quantum phenomena to perform calculations.","category":"science","source":"example"}},{"id":7643334340263966969,"payload":{"text":"Machine learning is a subset of AI focused on data-driven learning.","category":"technology","source":"example"}}],"next_page_offset":null},"status":"ok","time":0.000324771}

After serve.yaml and configmap

This configuration will now:

Initialize both the vLLM engine and the Qdrant client.
For each incoming request, it will: a. Query the Qdrant vector database for relevant context. b. Enhance the user's prompt with this context. c. Pass the enhanced prompt to the language model. d. Return the generated response.
