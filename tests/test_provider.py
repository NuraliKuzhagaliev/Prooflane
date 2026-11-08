import json
import httpx
import pytest
from prooflane.provider import ProviderError, VultrProvider


def test_provider_fail_closed_without_key(monkeypatch):
    monkeypatch.delenv("VULTR_INFERENCE_API_KEY", raising=False)
    monkeypatch.delenv("VULTR_MODEL", raising=False)
    with pytest.raises(ProviderError, match="Configure"):
        VultrProvider().generate("test", 1)


def test_provider_contract_and_no_raw_records(monkeypatch):
    """Mock HTTP contract, not a real Vultr integration test."""
    monkeypatch.setenv("VULTR_INFERENCE_API_KEY", "test-only-not-real")
    monkeypatch.setenv("VULTR_MODEL", "test-model")
    original = httpx.Client
    def respond(request):
        body = json.loads(request.content)
        assert str(request.url) == "https://api.vultrinference.com/v1/chat/completions"
        assert body["max_completion_tokens"] == 4096
        assert body["response_format"] == {"type": "json_object"}
        assert "reasoning" not in body  # unknown models retain their original profile
        assert json.loads(body["messages"][1]["content"]) == {"question":"find variance", "validated_record_count":24}
        return httpx.Response(200, json={"id":"chatcmpl-test", "model":"test-model", "choices":[{"finish_reason":"stop","message":{"content":json.dumps({"plan":["compute"],"code":"print('test')"})}}]})
    monkeypatch.setattr(httpx, "Client", lambda **kw: original(transport=httpx.MockTransport(respond), **kw))
    result = VultrProvider().generate("find variance",24)
    assert result["code"] == "print('test')"
    assert result["request_id"] == "chatcmpl-test"


@pytest.mark.parametrize('method', ['generate', 'explain'])
def test_deepseek_bounded_json_disables_default_thinking_without_raising_token_cap(monkeypatch, method):
    monkeypatch.setenv('VULTR_INFERENCE_API_KEY', 'test-only-not-real')
    monkeypatch.setenv('VULTR_MODEL', 'deepseek-v4.1-flash-1017')
    original = httpx.Client
    def respond(request):
        body = json.loads(request.content)
        assert body['reasoning'] == {'effort': 'none'}
        assert body['max_completion_tokens'] == (4096 if method == 'generate' else 1024)
        content = {'plan': ['Compute checked formula'], 'code': 'print(1)'} if method == 'generate' else {'lead': 'variance', 'review': 'contracts'}
        return httpx.Response(200, json={'id': 'chatcmpl-test', 'choices': [{'finish_reason': 'stop', 'message': {'content': json.dumps(content)}}]})
    monkeypatch.setattr(httpx, 'Client', lambda **kw: original(transport=httpx.MockTransport(respond), **kw))
    provider = VultrProvider()
    result = provider.generate('find variance', 7) if method == 'generate' else provider.explain(7, 5)
    assert result['request_id'] == 'chatcmpl-test'


def test_truncated_reply_is_never_used_as_executable_code(monkeypatch):
    monkeypatch.setenv('VULTR_INFERENCE_API_KEY', 'test-only-not-real')
    monkeypatch.setenv('VULTR_MODEL', 'deepseek-v4.1-flash-1017')
    original = httpx.Client
    def respond(request):
        return httpx.Response(200, json={'choices': [{'finish_reason': 'length', 'message': {'content': '{"code":"incomplete'}}]})
    monkeypatch.setattr(httpx, 'Client', lambda **kw: original(transport=httpx.MockTransport(respond), **kw))
    with pytest.raises(ProviderError, match='finish_reason=length'):
        VultrProvider().generate('find variance', 7)


def test_explanation_uses_only_checked_counts_and_rejects_unavailable_review(monkeypatch):
    monkeypatch.setenv("VULTR_INFERENCE_API_KEY", "test-only-not-real")
    monkeypatch.setenv("VULTR_MODEL", "test-model")
    original = httpx.Client

    def respond(request):
        body = json.loads(request.content)
        assert body["max_completion_tokens"] == 1024
        assert json.loads(body["messages"][1]["content"]) == {"verified_records": 7, "positive_differences": 0}
        content = json.dumps({"lead": "variance", "review": "contracts"})
        return httpx.Response(200, json={"choices": [{"finish_reason": "stop", "message": {"content": content}}]})

    monkeypatch.setattr(httpx, "Client", lambda **kw: original(transport=httpx.MockTransport(respond), **kw))
    with pytest.raises(ProviderError, match="unsupported explanation"):
        VultrProvider().explain(7, 0)


@pytest.mark.parametrize("envelope", [None, [], {"choices":[None]}, {"choices":["bad"]},
    {"choices":[{"message":None}]}, {"choices":[]}, {"choices":{}}])
def test_malformed_provider_envelope_fails_closed(monkeypatch, envelope):
    monkeypatch.setenv("VULTR_INFERENCE_API_KEY", "test-only-not-real")
    monkeypatch.setenv("VULTR_MODEL", "test-model")
    original = httpx.Client
    monkeypatch.setattr(httpx, "Client", lambda **kw: original(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, json=envelope)), **kw))
    with pytest.raises(ProviderError, match="invalid code plan"):
        VultrProvider().generate("test", 1)


@pytest.mark.parametrize("bad_field", ["plan", "model", "code"])
def test_provider_rejects_unpaired_unicode_before_execution(monkeypatch, bad_field):
    """Escaped invalid Unicode can arrive inside otherwise valid HTTP JSON."""
    monkeypatch.setenv("VULTR_INFERENCE_API_KEY", "test-only-not-real")
    monkeypatch.setenv("VULTR_MODEL", "test-model")
    plan = {"plan": ["Compute"], "code": "print('test')"}
    model = "test-model"
    if bad_field == "plan":
        plan["plan"] = ["\ud800"]
    elif bad_field == "code":
        plan["code"] = "\ud800"
    else:
        model = "\ud800"
    envelope = {"model": model, "choices": [{"finish_reason": "stop", "message": {"content": json.dumps(plan)}}]}
    original = httpx.Client
    monkeypatch.setattr(httpx, "Client", lambda **kw: original(transport=httpx.MockTransport(
        lambda request: httpx.Response(200, content=json.dumps(envelope).encode("utf-8"))), **kw))
    with pytest.raises(ProviderError, match="invalid code plan; no code was executed"):
        VultrProvider().generate("test", 1)
