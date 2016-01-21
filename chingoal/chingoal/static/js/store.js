    function unlock(id, unlock) {
        var val = parseInt(document.getElementById(id).value,10);
        if ((val - unlock) > 1) {
            alert("Please unlock in order!");
        } else {
            var r = confirm("Cost $5 to unlock lesson "+val+"?");
            if (r == true) {
                location.href = "unlock-learning/"+val;
            }
        }
    }

    function buyTitle(num, title) {
        var titles = ["Pupil","Freshman","Sophomore","Junior","Senior","Graduate"];
        if (title == titles[num]) {
            alert("This is your current title!");
        } else if (num == 0) {
            var r = confirm("Free to buy title Pupil");
            if (r == true) { 
                location.href = "buy-title/"+titles[num]+"/"+0; 
            }
        } else {
        var cost = 2 + num;
        var r = confirm("Cost $"+cost+" to buy title "+titles[num]+"?");
        if (r == true) { 
            location.href = "buy-title/"+titles[num]+"/"+cost; 
        }
        }
                    
    }