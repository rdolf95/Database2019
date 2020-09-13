$(document).ready(() => {
  // var container = document.getElementById('map'); //지도를 담을 영역의 DOM 레퍼런스
  var container = $("#map").get(0)
  var options = { //지도를 생성할 때 필요한 기본 옵션
    center: new kakao.maps.LatLng(33.450701, 126.570667), //지도의 중심좌표.
    level: 3 //지도의 레벨(확대, 축소 정도)
  };

  var map = new kakao.maps.Map(container, options);

  $("#position").submit((e) => {
    e.preventDefault()
    console.log("모야")
    console.dir(e.target.lat.value)
    console.log(typeof e.target.lat.value)
  })

  $("#here").click(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition((position) => {
        console.log(position.coords.latitude)
        console.log(position.coords.longitude)
      });
    } else {
      x.innerHTML = "Geolocation is not supported by this browser.";
    }
  })
})

