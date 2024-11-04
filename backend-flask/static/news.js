function ajax_get_data() {
    $.ajax({
    	url:"/newsItem",
        type:"post",
        dataType:"json",
        data:{"None" : "None"},
        success: function(data){
			console.log(data);
			if(data == 1 || data == "1") {
			    alert("뉴스 정보를 불러오는데 실패하였습니다.");
			    return;
			}

            document.getElementById("msg").remove();

            // 가져온 json 데이터 파싱 후 forEach문으로 table 출력
            write_data(data);
        },
        error: function(request, status, error) {
			alert("비동기 요청 중 오류가 발생했습니다.");
			console.log("code : " + request.status);
			console.log("message : " + request.responseText);
			console.log("error : " + error);
		}
	});
}


function write_data(result) {
    const container = document.getElementById("main-area");
    result.forEach(function(company) {
        let hr = document.createElement("hr");
        container.appendChild(hr);

        company.forEach(function(news) {
            let value =  `${news.date} : ${news.title}`
            let a = document.createElement("a");
            a.textContent = value;

            container.appendChild(a);

            let br = document.createElement("br");
            container.appendChild(br);
        });
    });
}