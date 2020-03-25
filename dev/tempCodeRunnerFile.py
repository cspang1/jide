col = math.floor(event.pos().x())
            row = math.floor(event.pos().y())
            self.last_pos = (row, col)
            self.scene.pixelClicked(self.root, row, col)