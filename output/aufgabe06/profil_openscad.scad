difference() {
	minkowski() {
		cube(center = true, size = [39.0, 39.0, 0.5]);
		cylinder($fn = 32, h = 0.5, r = 3.0);
	}
	rotate(a = 0) {
		translate(v = [0, 16.25, 0]) {
			cube(center = true, size = [10.0, 12.5, 2]);
		}
	}
	rotate(a = 0) {
		translate(v = [0, 9.0, 0]) {
			cube(center = true, size = [16.5, 2.0, 2]);
		}
	}
	rotate(a = 90) {
		translate(v = [0, 16.25, 0]) {
			cube(center = true, size = [10.0, 12.5, 2]);
		}
	}
	rotate(a = 90) {
		translate(v = [0, 9.0, 0]) {
			cube(center = true, size = [16.5, 2.0, 2]);
		}
	}
	rotate(a = 180) {
		translate(v = [0, 16.25, 0]) {
			cube(center = true, size = [10.0, 12.5, 2]);
		}
	}
	rotate(a = 180) {
		translate(v = [0, 9.0, 0]) {
			cube(center = true, size = [16.5, 2.0, 2]);
		}
	}
	rotate(a = 270) {
		translate(v = [0, 16.25, 0]) {
			cube(center = true, size = [10.0, 12.5, 2]);
		}
	}
	rotate(a = 270) {
		translate(v = [0, 9.0, 0]) {
			cube(center = true, size = [16.5, 2.0, 2]);
		}
	}
	cylinder($fn = 64, center = true, h = 2, r = 3.4);
}
