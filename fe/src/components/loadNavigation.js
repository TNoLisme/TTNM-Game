fetch("/src/pages/navigation.html")
  .then(res => res.text())
  .then(data => {
    document.getElementById("navi").innerHTML = data;
  });
