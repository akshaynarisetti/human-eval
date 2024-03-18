import concurrent.futures
from human_eval.data import write_jsonl, read_problems
from openai import OpenAI

client = OpenAI(api_key="sk-****")

def generate_one_completion(prompt):
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    return completion.choices[0].message.content.strip()

def generate_completions_for_task(task_id, num_samples):
    completions = []
    for i in range(num_samples):
        print(f"Generating completion {i+1}/{num_samples} for task: {task_id}")
        completion = generate_one_completion(problems[task_id]["prompt"])
        completions.append(dict(task_id=task_id, completion=completion))
        print(f"Generated completion: {completion}")
    return completions

problems = read_problems()
print(f"Number of problems: {len(problems)}")

num_samples_per_task = 200
with concurrent.futures.ThreadPoolExecutor() as executor:
    futures = []
    for task_id in problems:
        print(f"Submitting task: {task_id}")
        future = executor.submit(generate_completions_for_task, task_id, num_samples_per_task)
        futures.append(future)

    samples = []
    for future in concurrent.futures.as_completed(futures):
        completions = future.result()
        samples.extend(completions)

print(f"Number of generated completions: {len(samples)}")
write_jsonl("chatgpt_samples.jsonl", samples)
print("Completions written to chatgpt_samples.jsonl")