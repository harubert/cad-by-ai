projection(cut = true) {
	difference() {
		minkowski() {
			cube(center = true, size = [31.0, 31.0, 0.5]);
			cylinder($fn = 64, h = 0.5, r = 4.5);
		}
		rotate(a = 0) {
			translate(v = [0, 14.875, 0]) {
				cube(center = true, size = [8.0, 10.25, 2]);
			}
		}
		rotate(a = 0) {
			translate(v = [0, 8.75, 0]) {
				cube(center = true, size = [12.0, 2.0, 2]);
			}
		}
		rotate(a = 90) {
			translate(v = [0, 14.875, 0]) {
				cube(center = true, size = [8.0, 10.25, 2]);
			}
		}
		rotate(a = 90) {
			translate(v = [0, 8.75, 0]) {
				cube(center = true, size = [12.0, 2.0, 2]);
			}
		}
		rotate(a = 180) {
			translate(v = [0, 14.875, 0]) {
				cube(center = true, size = [8.0, 10.25, 2]);
			}
		}
		rotate(a = 180) {
			translate(v = [0, 8.75, 0]) {
				cube(center = true, size = [12.0, 2.0, 2]);
			}
		}
		rotate(a = 270) {
			translate(v = [0, 14.875, 0]) {
				cube(center = true, size = [8.0, 10.25, 2]);
			}
		}
		rotate(a = 270) {
			translate(v = [0, 8.75, 0]) {
				cube(center = true, size = [12.0, 2.0, 2]);
			}
		}
		cylinder($fn = 64, center = true, h = 2, r = 3.4);
		translate(v = [14.75, 14.75, 0]) {
			cube(center = true, size = [6.5, 6.5, 2]);
		}
		translate(v = [14.75, -14.75, 0]) {
			cube(center = true, size = [6.5, 6.5, 2]);
		}
		translate(v = [-14.75, 14.75, 0]) {
			cube(center = true, size = [6.5, 6.5, 2]);
		}
		translate(v = [-14.75, -14.75, 0]) {
			cube(center = true, size = [6.5, 6.5, 2]);
		}
	}
}
