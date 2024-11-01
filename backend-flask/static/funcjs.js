// 첫번째 버튼 클릭 함수
document.getElementById("btnvalue1").addEventListener("click", function() {
    let value1 = document.getElementById("value1");

    // 공백 검사
    if(value1.value == "") {
        alert("검색어를 입력해주세요.");
        value1.focus();
        return false;
    }

    // ajax 요청
    $.ajax({
    	url:"/queryItem",
        type:"post",
        dataType:"text",
        data:{"value1" : value1.value},
        success: function(data){
			writeItem(data);
        },
        error: function(request, status, error) {
			alert("비동기 요청 중 오류가 발생했습니다.");
			console.log("code : " + request.status);
			console.log("message : " + request.responseText);
			console.log("error : " + error);
		}
	});

});




function writeItem(data) {
    console.log(data);
    document.getElementById("wc-img").src = "static/wc-img/" + data;
    $(data).each(function() {
    })
}
