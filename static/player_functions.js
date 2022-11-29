
// init variables

function init_playlist(JSON_input){	
	playlist_obj=JSON.parse(JSON_input)
	playlist_length = Math.ceil(Object.keys(playlist_obj).length / 2)
}
var playlist_length;
var playlist_obj;
var playlist_on=false;
var playlist_track_num=0;

	// Create an event listener to dynamicly update player when clickilng the progress-bar.
window.onload= function(){
var player=document.getElementById('player');
var progBar=document.getElementById("progress-bar");
var progress=document.getElementById("progress");
console.log("progress.offsetWidth: "+progress.offsetWidth);
progress.addEventListener('click', function(e) {
		var pct = ((e.offsetX / progress.offsetWidth)*100);
		console.log("pct="+pct);
		if (player.getAttribute('src')){
			progBar.style.width = pct + "%";
			player.currentTime=pct*player.duration/100;
			}
	}, false);
}


// operation functions:

	// start the playlist.
function playlist(){
	if (playlist_obj){
		document.getElementById('playing_status').innerHTML='on'
		playlist_on=true;
		playlist_track_num=0;
		playlist_next(playlist_track_num,playlist_obj,true);
		document.getElementById('p').innerHTML="playlist length = "+String(playlist_length);
	}
	else {
		console.log("No playlist_obj Error")
	}
}

	// auto play next track on playlist.
function playlist_next(i,playlist_obj,first){
	console.log("doing playlist_next(i) of: (starting at 0) i="+i)
	if (i<playlist_length && playlist_on) {
		song_id=playlist_obj[i];
		filename=playlist_obj[song_id];
		playlist_track_num=i;
		play(filename);
	}
	else{
		playlist_on=false;
		console.log("playlist ended \n playlist_on="+playlist_on);
		
		abort()
	}
}

	// play file.
function play(filename="",specifier=false){
	if (specifier){
		for (let trk=0; trk<playlist_obj.length/2; trk++){
			if (playlist_obj[playlist_obj[trk]]==filename){
				playlist_track_num=trk;
				console.log("trk="+trk)
				break;
			}
		}
	}
	player=document.getElementById('player');
	if (filename.length){	
		document.getElementById('playing_title').innerHTML=filename.replace(".mp3",'').replace(/[^a-z0-9]/gi, ' ');
		track="static/uploads/"+filename;
		player.setAttribute('src',track);
		player.load();
		playPromise=player.play();
		if (document.getElementById('playing_status').innerHTML=='off' || playlist_on==false){
			document.getElementById('playing_status').innerHTML='on';
			playlist_on=true;
		}

		if (playPromise !== undefined) {
		playPromise.then(_ => {
			console.log("play() successful filename = "+filename);
			player.currentTime=0;
			render_progBar();
			if (playlist_on && playlist_track_num<playlist_length){
				
				player.onended = function(){ playlist_next(playlist_track_num+1,playlist_obj,false); };
				console.log((playlist_track_num)+"'th onended event declared playlist_next("+(playlist_track_num)+")");
			}
			
		})
			.catch(error => {
				console.log("play() errored -> "+error)
			});
		  }
	}
	else{
		if (player.paused && player.getAttribute("src")){
			playPromise=player.play();
			if (playPromise !== undefined) {
			playPromise.then(_ => {
				console.log("play() successful on filename = "+filename);
				render_progBar();
				})
				.catch(error => {
					console.log("play() errored -> "+error)
				});
			}
			 else{
				console.log("playpromise undifined");
			}
		}
		else if (player.paused && !player.getAttribute("src")){
			playlist()
		}
		else {
			console.log("pause() successful");
			player.pause();
		}
	}
}


	// Render dynamic progress-bar and time display.
function render_progBar(doInterval=true){
	var player=document.getElementById('player');
	var progBar=document.getElementById("progress-bar");
	let d=player.duration;
	console.log('d='+d)
	if (isNaN(d)){
		d=0
		console.log('d was NaN string and now is =0')
	}
	document.getElementById("duration").innerHTML=Math.round(d/60).toLocaleString('en-US', {minimumIntegerDigits: 2})+':'+Math.round(d % 60).toLocaleString('en-US', {minimumIntegerDigits: 2});
	var timer=setInterval(update,100);
	for (let i = 1; i < timer; i++) {
		window.clearInterval(i);
	  }
	function update(){
		let t=100*player.currentTime/player.duration
		//console.log(t)
		progBar.style.width= String(t)+"%"
		document.getElementById("currentTime").innerHTML=Math.floor(player.currentTime/60 % 60).toLocaleString('en-US', {minimumIntegerDigits: 2})+':'+Math.floor(player.currentTime%60).toLocaleString('en-US', {minimumIntegerDigits: 2});
		
	}
}
 
 
	// jump to next song.
function next(){
	if (playlist_on && playlist_track_num<playlist_length){
		player=document.getElementById('player')
		playlist_track_num++;
		song_id=playlist_obj[playlist_track_num]
		filename=playlist_obj[song_id]
		play(filename);
	}
}

	// jump to privious song 
function previous(){
	if (playlist_on && playlist_track_num>0){
		console.log("playlist_track_num"+playlist_track_num)
		document.getElementById('player')
		playlist_track_num--;
		song_id=playlist_obj[playlist_track_num]
		filename=playlist_obj[song_id]
		play(filename);
	}
	else{
		console.log("No previous track")
	}
}

	// stop song (return to 00:00 and pause)
function stop(){
	player=document.getElementById('player');
	player.currentTime=0;
	player.pause();
	render_progBar();
}

	//cancel active playlist (empty the audio ) 
function abort(){
	player=document.getElementById('player');
	playlist_on=false
	playlist_track_num=0;
	document.getElementById('playing_status').innerHTML='off';
	document.getElementById('playing_title').innerHTML='';
	player.pause();
	player.removeAttribute('src');

	render_progBar();
}

// function del(filename){
// 	console.log("deleting - "+filename);
// 	let song_id=playlist_obj[n];
// 	delete playlist_obj[song_id];
// 	delete playlist_obj[n];
// 	for (let i=n; i<playlist_length; i++){
// 		playlist_obj[i]=playlist_obj[i+1];
// 		delete playlist_obj[i+1];
// 	}
// 	playlist_length--;
// 	console.log(playlist_length);
// 	console.log(playlist_obj);
// }