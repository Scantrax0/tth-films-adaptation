class FilterController {
    constructor(videoId, filterName, dangerIntervals, callback) {
        this.videoId = videoId;
        this.el = document.getElementById(videoId);
        this.filterName = filterName;
        this.dangerIntervals = dangerIntervals;
        this.isTimeoutSet = false;
        this.callback = callback;
        this.isPlaying = false;
    }

    removeFilter() {
        if (this.isPlaying) {
            var el = document.getElementById(this.videoId);
            el.classList.remove(this.filterName);
            this.isTimeoutSet = false;
            console.log('filter removed');
        } else {
            this.isTimeoutSet = false;
            console.log('video paused: filter did not removed');
        }     
    }

    timeUpdate(time) {
        this.dangerIntervals.forEach(element => {
            if (!this.isTimeoutSet && element[0] < time + 0.3 && element[1] > time) {   
                var el = document.getElementById(this.videoId); 
                el.classList.add(this.filterName);
                this.isTimeoutSet = true;
                console.log('filter added');
                setTimeout(this.callback, (element[1] - time) * 1000, this);
                console.log('Set callback in ' + (element[1] - time));
            }
        });
    }    

    play() {
        this.isPlaying = true;
    }

    pause() {
        this.isPlaying = false;
    }
}