from kombu import Exchange, Queue

broker_url = 'redis://localhost:6379/0'
result_backend = 'redis://localhost:6379/0'

task_queues = (
    Queue('video_processing', routing_key='video_processing.#'),
)

task_default_queue = 'video_processing'
task_default_routing_key = 'video_processing.default'
