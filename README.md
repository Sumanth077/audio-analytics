# Audio Analytics Package

This project contains a Steamship Package that creates a search endpoint over audio files capable of filtering through
transcript, entities, and sentiments.

## Usage

```python
from steamship import Steamship, Tag

instance = Steamship.use("audio-analytics", "my-workspace-name")

url = "<url to mp3 file>"
analyze_task = instance.invoke("analyze_url", url=url).data

# Wait for completion
# See: examples/audio-analytics-python-client-demo.ipynb to see hows

# Query audio contents
# Note: more examples in examples/audio-analytics-python-client.demo.ipynb
query_tags = Tag.query(
    instance.client, 'kind "entity" and overlaps { kind "sentiment" and name "NEGATIVE" }'
).tags
unique_entities = {tag.name for tag in query_tags}
print(
    f"There are {len(unique_entities)} people who have been referenced in a negative context:"
)
print(" * " + "\n * ".join([tag.name for tag in query_tags]))
```

## Developing

Development instructions are located in [DEVELOPING.md](DEVELOPING.md)

## Testing

Testing instructions are located in [TESTING.md](TESTING.md)

## Deploying

Deployment instructions are located in [DEPLOYING.md](DEPLOYING.md)
