import app as yt_app


def test_request_download_returns_token(client, monkeypatch, tmp_path):
    yt_app.app.config.update(TESTING=True, DOWNLOAD_FOLDER=str(tmp_path))

    def fake_download(url, destination_folder):
        assert destination_folder == str(tmp_path)
        assert isinstance(url, str)
        return "x.mp3"

    monkeypatch.setattr(yt_app, "download_video_as_mp3", fake_download)

    res = client.post("/request_download", json={"url": "https://example.com/watch?v=abc"})
    assert res.status_code == 200

    payload = res.get_json()
    assert "token" in payload

    filename = yt_app.serializer.loads(payload["token"], salt="file-download", max_age=60 * 60)
    assert filename == "x.mp3"

    health = client.get("/healthz")
    assert health.status_code == 200


def test_request_download_missing_url_is_400(client):
    res = client.post("/request_download", json={})
    assert res.status_code == 400


def test_download_valid_token_serves_file(client, tmp_path):
    yt_app.app.config.update(TESTING=True, DOWNLOAD_FOLDER=str(tmp_path))
    (tmp_path / "x.mp3").write_bytes(b"hi")

    token = yt_app.serializer.dumps("x.mp3", salt="file-download")
    res = client.get(f"/download/{token}")

    assert res.status_code == 200
    assert res.data == b"hi"


def test_download_invalid_token_is_404(client):
    res = client.get("/download/not-a-token")
    assert res.status_code == 404
