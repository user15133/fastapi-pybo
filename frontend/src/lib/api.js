import qs from "qs";
import { access_token, username, is_login } from "./store";
import { get } from "svelte/store";
import { push } from "svelte-spa-router";

const fastapi = (operation, url, params, success_callback, failure_callback) => {
    let method = operation.toUpperCase();
    let content_type = "application/json";
    let body = null;

    if (operation === "login") {
        method = "POST";
        content_type = "application/x-www-form-urlencoded";
        body = qs.stringify(params);
    } else if (method !== "GET" && params) {
        body = JSON.stringify(params);
    }

    const baseUrl = import.meta.env.VITE_SERVER_URL || import.meta.env.VITE_SERVER_URL_LOCAL || "http://127.0.0.1:8000";
    let _url = baseUrl + url;

    if (method === "GET" && params && Object.keys(params).length > 0) {
        const queryParams = new URLSearchParams(params).toString();
        _url += `?${queryParams}`;
    }

    const options = {
        method: method,
        headers: {
            "Content-Type": content_type,
            "Accept": "application/json",
        },
    };

    const _access_token = get(access_token);
    if (_access_token) {
        options.headers["Authorization"] = "Bearer " + _access_token;
    }

    if (body) {
        options.body = body;
    }

    console.log("API 호출:", { url: _url, method, headers: options.headers, body, params });

    fetch(_url, options)
        .then(async (response) => {
            console.log("API 응답:", response); // 응답 디버깅
            let json = null;
            try {
                json = await response.json();
            } catch (error) {
                console.error("JSON 파싱 에러:", error);
                json = { error: "JSON 파싱 실패", status: response.status };
            }

            if (response.ok) {
                if (success_callback) success_callback(json);
            } else if (response.status === 422) {
                console.error("422 오류 발생: 요청 데이터가 유효하지 않습니다.", json);
                if (failure_callback) failure_callback(json);
                else alert("422 오류: 요청 데이터가 유효하지 않습니다.");
            } else if (response.status === 401) {
                access_token.set("");
                username.set("");
                is_login.set(false);
                alert("로그인이 필요합니다.");
                push("/user-login");
            } else {
                if (failure_callback) failure_callback(json);
                else console.error("API 호출 실패:", json);
            }
        })
        .catch((error) => {
            console.error("API 호출 에러:", error);
            if (failure_callback) failure_callback(error);
            else alert("오류 발생: " + error.message);
        });
};

export default fastapi;
