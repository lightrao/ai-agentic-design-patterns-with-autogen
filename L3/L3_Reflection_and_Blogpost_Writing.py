# %% [markdown]
# # Lesson 3: Reflection and Blogpost Writing

# %% [markdown]
# ## Setup

# %%
llm_config = {"model": "gpt-3.5-turbo"}

# %% [markdown]
# ## The task!

# %%
task = '''
        Write a concise but engaging blogpost about
       DeepLearning.AI. Make sure the blogpost is
       within 100 words.
       '''


# %% [markdown]
# ## Create a writer agent

# %%
import autogen

writer = autogen.AssistantAgent(
    name="Writer",
    system_message="You are a writer. You write engaging and concise " 
        "blogpost (with title) on given topics. You must polish your "
        "writing based on the feedback you receive and give a refined "
        "version. Only return your final work without additional comments.",
    llm_config=llm_config,
)

# %%
reply = writer.generate_reply(messages=[{"content": task, "role": "user"}])

# %%
print(reply)

# %% [markdown]
# ## Adding reflection 
# 
# Create a critic agent to reflect on the work of the writer agent.

# %%
critic = autogen.AssistantAgent(
    name="Critic",
    is_termination_msg=lambda x: x.get("content", "").find("TERMINATE") >= 0,
    llm_config=llm_config,
    system_message="You are a critic. You review the work of "
                "the writer and provide constructive "
                "feedback to help improve the quality of the content.",
)

# %%
res = critic.initiate_chat(
    recipient=writer,
    message=task,
    max_turns=2,
    summary_method="last_msg"
)

# %% [markdown]
# ## Nested chat

# %%
SEO_reviewer = autogen.AssistantAgent(
    name="SEO Reviewer",
    llm_config=llm_config,
    system_message="You are an SEO reviewer, known for "
        "your ability to optimize content for search engines, "
        "ensuring that it ranks well and attracts organic traffic. " 
        "Make sure your suggestion is concise (within 3 bullet points), "
        "concrete and to the point. "
        "Begin the review by stating your role.",
)


# %%
legal_reviewer = autogen.AssistantAgent(
    name="Legal Reviewer",
    llm_config=llm_config,
    system_message="You are a legal reviewer, known for "
        "your ability to ensure that content is legally compliant "
        "and free from any potential legal issues. "
        "Make sure your suggestion is concise (within 3 bullet points), "
        "concrete and to the point. "
        "Begin the review by stating your role.",
)

# %%
ethics_reviewer = autogen.AssistantAgent(
    name="Ethics Reviewer",
    llm_config=llm_config,
    system_message="You are an ethics reviewer, known for "
        "your ability to ensure that content is ethically sound "
        "and free from any potential ethical issues. " 
        "Make sure your suggestion is concise (within 3 bullet points), "
        "concrete and to the point. "
        "Begin the review by stating your role. ",
)

# %%
meta_reviewer = autogen.AssistantAgent(
    name="Meta Reviewer",
    llm_config=llm_config,
    system_message="You are a meta reviewer, you aggragate and review "
    "the work of other reviewers and give a final suggestion on the content.",
)

# %% [markdown]
# ## Orchestrate the nested chats to solve the task

# %%
def reflection_message(recipient, messages, sender, config):
    """
    Generates a review prompt for a reviewer agent.
    This function is called by the autogen framework during nested chat orchestration.
    Args:
        recipient: The reviewer agent (SEO_reviewer, LegalReviewer, or EthicsReviewer) that will receive the message.
        messages: The message history of the overall chat.
        sender: The Critic agent, who is sending the review request.
        config: Configuration settings (not used in this function).
    Returns:
        A string containing the review prompt, including the content to be reviewed.
    """
    print(f"recipient: {recipient.name}")
    print(f"sender: {sender.name}")
    print(f"messages: {messages}")
    print(f"config: {config}")
    
    return f'''Review the following content.
            \n\n {recipient.chat_messages_for_summary(sender)[-1]['content']}'''

review_chats = [
    {
     "recipient": SEO_reviewer, 
     "message": reflection_message, 
     "summary_method": "reflection_with_llm",
     "summary_args": {"summary_prompt" : 
        "Return review into as JSON object only:"
        "{'Reviewer': '', 'Review': ''}. Here Reviewer should be your role",},
     "max_turns": 1},
    {
    "recipient": legal_reviewer, "message": reflection_message, 
     "summary_method": "reflection_with_llm",
     "summary_args": {"summary_prompt" : 
        "Return review into as JSON object only:"
        "{'Reviewer': '', 'Review': ''}.",},
     "max_turns": 1},
    {"recipient": ethics_reviewer, "message": reflection_message, 
     "summary_method": "reflection_with_llm",
     "summary_args": {"summary_prompt" : 
        "Return review into as JSON object only:"
        "{'reviewer': '', 'review': ''}",},
     "max_turns": 1},
     {"recipient": meta_reviewer, 
      "message": "Aggregrate feedback from all reviewers and give final suggestions on the writing.", 
     "max_turns": 1},
]


# %%
critic.register_nested_chats(
    review_chats,
    trigger=writer,
)

# %% [markdown]
# **Note**: You might get a slightly different response than what's shown in the video. Feel free to try different task.

# %%
res = critic.initiate_chat(
    recipient=writer,
    message=task,
    max_turns=2,
    summary_method="last_msg"
)

# %% [markdown]
# ## Get the summary

# %%
print(res.summary)


