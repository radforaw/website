def FindLineCircleIntersections(p,point1, point2):
	cx,cy,radius= p
	dx = point2[0] - point1[0]
	dy = point2[1] - point1[1]

	A = dx * dx + dy * dy
	B = 2 * (dx * (point1[0] - cx) + dy * (point1[1] - cy))
	C = (point1[0] - cx) * (point1[0] - cx) + (point1[1] - cy) * (
		point1[1] - cy) - radius * radius

	det = B * B - 4 * A * C
	if (A <= 0.0000001) or (det < 0):
		return []
	elif det == 0:
		t = -B / (2 * A)
		intersection1 = (point1[0] + t * dx, point1[1] + t * dy)
		return [intersection1]
	else:
		t = (-B + math.sqrt(det)) / (2 * A)
		intersection1 = (point1[0] + t * dx, point1[1] + t * dy)
		t = (-B - math.sqrt(det)) / (2 * A)
		intersection2 = (point[0] + t * dx, point[1] + t * dy)
		return [intersection1, intersection2]

