document.addEventListener('DOMContentLoaded', function() {
	
	let pagenumber = 1;

	try {
		const temp = document.querySelector('#currentUser');
		document.querySelector('#currentUser').addEventListener('click', () => profile(document.querySelector('#currentUser').text));
		document.querySelector('#newPost-form').addEventListener('submit', post);
		document.querySelector('#followPosts').addEventListener('click', () => pre_posts('followers', 1));
		document.querySelector('#newPost').style.display = 'block';	
		document.querySelector('#profile').style.display = 'none';	

		pre_posts('all', pagenumber);
	} catch {
		document.querySelector('#newPost').style.display = 'none';
		document.querySelector('#profile').style.display = 'none';
	
		pre_posts('all', pagenumber);
	}
})

	
function pre_posts(pick, pagenumber) {
	
	document.querySelector('#previous').addEventListener('click', () => {
		pagenumber--;
		load_posts(pick, pagenumber);
		console.log("you are on page: " + pagenumber);
	});
	document.querySelector('#next').addEventListener('click', () => {
		pagenumber++;
		load_posts(pick, pagenumber);
		console.log("you are on page: " + pagenumber);
	});
	
	if (pick == 'followers') {
		document.querySelector('#newPost').style.display = 'none';
		document.querySelector('#profile').style.display = 'none';
	} else {
		document.querySelector('#newPost').style.display = 'block';
	}
	load_posts(pick, pagenumber);
}


function load_posts(pick, pagenumber) {
	console.log(pick);
	let currentUser = "";
	try {
		currentUser = document.querySelector('#currentUser').text;
	} catch {
			currentUser = "not inlogged";
	}
	if (pagenumber == 1) {
		document.querySelector('#previous').style.display = 'none';
	}
	else {
		document.querySelector('#previous').style.display = 'block';
	}
	

	fetch(`/posts/${pick}`, {
		method: 'PUT',
		body: JSON.stringify({
			page: pagenumber
		})
	})
	.then(response => response.json())
	.then(result => {

		document.querySelector('#posts-div2').innerHTML = '';
		const lastpage = result.lastpage;
		if (lastpage == pagenumber) {
			document.querySelector('#next').style.display = 'none';
		}
		else {
			document.querySelector('#next').style.display = 'block';
		}
		console.log(lastpage);
		result.posts.forEach(post =>{
			
			const element = document.createElement('div');
			element.setAttribute("class", "post-div");
			
			const publisher = document.createElement('div');
			publisher.setAttribute("class", "publisher");
			publisher.innerHTML = post.user;
			publisher.addEventListener('click', () => profile(post.user));
			element.append(publisher);

			if (currentUser == post.user) {
				const edit = document.createElement('div');
				edit.setAttribute("class", "edit");
				edit.innerHTML = "Edit";
				edit.addEventListener('click', function() {
					element.innerHTML = '';
					const text = document.createElement('textarea');
					text.setAttribute("class", "form-control");
					text.setAttribute("id", "editPost-body");
					text.innerHTML = post.body;
					const input = document.createElement('button');
					input.setAttribute("class", "btn btn-primary");
					input.innerHTML = "Save";
					input.addEventListener('click', function() {
						fetch(`/posts/edit/${post.id}`, {
							method: 'PUT',
							body: JSON.stringify({
								body: document.querySelector('#editPost-body').value
							})
						})
						.then(response => response.json())
						.then(result => {
							console.log(result)
							pre_posts('all', pagenumber)
						});
					})
					element.append(text);
					element.append(input);	
				})
				element.append(edit);
			} else {
				const like = document.createElement('div');
				like.setAttribute("class", "edit");
				fetch(`/posts/like/${post.id}`, {
							method: 'GET'})
				.then(response => response.json())
				.then(result => {
					if (result.message == 'liking') {
						like.innerHTML = "Unlike";
					} else if (result.message == 'not liking') {
						like.innerHTML = "Like";
					} else {
						console.log('Error in Json message.')
					}
				})
				element.append(like);
				like.addEventListener('click', function() {
					fetch(`/posts/like/${post.id}`, {
							method: 'PUT'})
					.then(response => response.json())
					.then(result => {
						console.log(result);
						pre_posts(pick, pagenumber)
					})
				})
			}

			const body = document.createElement('div');
			body.innerHTML = post.body;
			element.append(body);

			const likes = document.createElement('div');
			likes.innerHTML = post.like + ' likes';
			element.append(likes);

			const timestamp = document.createElement('div');
			timestamp.setAttribute("class", "timestamp");
			timestamp.innerHTML = post.timestamp;
			element.append(timestamp);

			document.querySelector('#posts-div2').append(element);

		})
	})

	
}

function post(event) {
	const body = document.querySelector('#newPost-body').value;
	document.querySelector('#newPost-body').value = "";

	fetch('/posts', {
		method: 'POST',
		body: JSON.stringify({
			body: body
		})
	})
	.then(response => response.json())
	.then(result => {
		console.log(result);
		pre_posts('all', 1)
	});
	event.preventDefault();
}

function profile(name) {

	try {
		const currentUser = document.querySelector('#currentUser').text;

		let countFollowers = 0;
		let countFollowing = 0;
		

		document.querySelector('h1').innerHTML = name;
		pre_posts(name, 1)
		
		document.querySelector('#newPost').style.display = 'none';
		document.querySelector('#profile').style.display = 'block';
		if (name == currentUser) {
			document.querySelector('#followButton-div').style.display = "none";
		}
		fetch(`/numbers/${name}`)
		.then(response => response.json())
		.then(results => {
			//console.log(results);
			results.forEach(entry =>{
				if (entry.user == name) {
					countFollowing++;
				}
				if (entry.following == name) {
					countFollowers++;
				}
			})
			document.querySelector('#followerNumber').innerHTML = countFollowers;
			document.querySelector('#followingNumber').innerHTML = countFollowing;
		})
		
		button = document.querySelector('#followButton')
		fetch(`/follow/${name}`, {
			method: 'GET'
		})
		.then(response => response.json())
		.then(following => {
			console.log(following);
			if (following.message == "not following") {
				button.innerHTML = "Follow"
			} else if (following.message == "following") {
				button.innerHTML = "Unfollow"
			}
		})
		button.addEventListener('click', () => {
			if (button.innerHTML == "Follow") {
				fetch(`/follow/${name}`, {
					method: 'POST'
				})
				.then(results => {
					console.log(results);
					document.querySelector('#followButton').innerHTML = "Unfollow";
					//profile(name)
					countFollowers++;
					document.querySelector('#followerNumber').innerHTML = countFollowers;
		        })
	       	
			} else if (button.innerHTML == "Unfollow") {
				fetch(`/follow/${name}`, {
					method: 'PUT'
				})
				.then(results => {
					console.log(results);
					document.querySelector('#followButton').innerHTML = "Follow";
					//profile(name)
		        	countFollowers--;
					document.querySelector('#followerNumber').innerHTML = countFollowers;
		        })
	       	
			} else {
				console.log("Error in button addEventListener");

			}
		});
	} catch {
		window.location.pathname = "/login";
	}
	

}
