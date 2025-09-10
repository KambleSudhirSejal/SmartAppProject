const toggleBtn=document.getElementById("toggleBtn");
const getStatusText = document.getElementById("status");

const intensitySlider = document.getElementById("IntensitySlider");
const intensityValue =document.getElementById("IntensityValue");

let toggleState=0;
let intensityState=50;


function publishState(){
        fetch("/publish",{
        method:'POST',
        headers:{
                "Content-Type": "application/json"
        },
            body:JSON.stringify({"toggle":toggleState,"intensity":intensityState})
    })
.then(res => res.json())
.then(data => console.log("server:",data))
.catch(err => console.log("Error",err))



}

toggleBtn.addEventListener("change", function(){
        toggleState=this.checked ? 1 : 0;
        getStatusText.innerText=this.checked ? "ON" : "OFF";
        publishState();
    });

intensitySlider.addEventListener("change",function(){
    intensityState=parseInt(this.value)
    intensityValue.innerText=intensityState
      if (toggleState === 1) {  // only publish when ON
        publishState();
    }
});

//fetch mqtt values periodically and update the UI
function fetchState(){
    fetch("/get_state")
    .then(res => res.json())
    .then(data => {
        console.log("fetch data ",data)
        toggleBtn.checked = (data.toggle===1);
        getStatusText.innerHTML=toggleBtn.checked ? "ON" : "OFF"
        
        if(intensitySlider !== undefined){
                    intensitySlider.value=data.intensity;
                    intensityValue.innerText=data.intensity;
                    addToChart(data.intensity)
        }
    })
    .catch(err => console.log("Error fetching state: ",err));
}

  

const ctx = document.getElementById("myChart").getContext("2d");
const myChart = new Chart(ctx, {
    type: "line",
    data: {
        labels: [],
        datasets: [{
            label: "Power Consumption",
            borderColor: "blue",
            backgroundColor: "rgba(0,0,255,0.1)",
            data: [],
            fill: false,
            tension: 0.3  // smooth line
        }]
    },
    options: {
        responsive: true,
        plugins: {
            legend: {
                display: false
            },
            title: {
                display: true,
                text: "Data shown through MQTT"
            }
        },
        scales: {
            x: {
                title: { display: true, text: "Hour of Day" }
            },
            y: {
                title: { display: true, text: "Power (W)" },
                beginAtZero: true
            }
        }
    }
});




function get_power_data(){
    fetch("/devices/hourly")
    .then(res => res.json())
    .then(data =>{
        const labels = data.map(d => d.hour);
        const values = data.map(d => d.power);

        myChart.data.labels=labels;
        myChart.data.datasets[0].data=values
        myChart.update()
    })
    .catch(err => console.error("Error fetching power data:", err));
}
get_power_data()
setInterval(fetchState,2000)















