function ajax_get_data() {
    // count view
    count_value(8);

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
            write_news_data(data);
        },
        error: function(request, status, error) {
			alert("비동기 요청 중 오류가 발생했습니다.");
			console.log("code : " + request.status);
			console.log("message : " + request.responseText);
			console.log("error : " + error);
		}
	});
}


// html에 작성
function write_news_data(result) {
    const container = document.getElementById("news-list");

    result.forEach(function(company) {
        company.forEach(function(news) {
            const html = `
            <table id="table_1" class="table table-striped" style="width:40%;">
            <thead>
                <tr>
                    <th scope="col" colspan="2">ㅇㅇ일보</th>
                </tr>
                <tr>
                    <th scope="col">날짜</th>
                    <th scope="col">뉴스 제목</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <th scope="row" style="vertical-align: middle;">${news.date}</th>th>
                    <td><a href="${news.link}" target="_blank">${news.title}</a></td>
                </tr>
            </tbody>
            </table>
        `;

        container.insertAdjacentHTML('beforeend', html);
        });
    });
}


// 임시 카운터
function count_value(time) {
    let what = document.getElementById("msg");

	try {
        var x = setInterval(function() {
			what.innerHTML = "데이터를 가져오는 중입니다... " + time + "초";
			time--;

			if(time<0) {
				clearInterval(x);
				what.innerHTML = "데이터를 가져오는 중입니다... 0초";
			}
		}, 1000);
	} catch (error) {
		console.log(error);
	}
}