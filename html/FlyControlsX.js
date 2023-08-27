import * as THREE from "three";
import { PointerLockControls } from "three/addons/controls/PointerLockControls.js";

class FlyControlsX extends PointerLockControls {
    constructor(camera, domElement) {
        super(camera, domElement);

        this.speed = 2000;
        this.minSpeed = 50;
        this.relativeUp = false;

        this.prevTime = performance.now();

        this.doMoveForward = false;
        this.doMoveBackward = false;
        this.doMoveLeft = false;
        this.doMoveRight = false;
        this.doMoveDown = false;
        this.doMoveUp = false;

        document.addEventListener("keydown", this.onKeyDown.bind(this));
        document.addEventListener("keyup", this.onKeyUp.bind(this));
        document.addEventListener("wheel", this.wheel.bind(this));
        domElement.addEventListener("click", this.click.bind(this));
    }

    update() {
        const time = performance.now();

        if(this.isLocked === true) {
            const delta = (time - this.prevTime) / 1000;

            let direction = new THREE.Vector3();
            direction.z = (Number(this.doMoveForward) - Number(this.doMoveBackward)) * -1; // Forward is negative value
            direction.x = Number(this.doMoveRight) - Number(this.doMoveLeft);
            if (this.relativeUp) {
                direction.y = Number(this.doMoveUp) - Number(this.doMoveDown);
            } else {
                this.camera.position.y += (Number(this.doMoveUp) - Number(this.doMoveDown)) * delta * this.speed;
            }

            direction.applyQuaternion(this.camera.quaternion);
            this.camera.position.addScaledVector(direction, delta * this.speed)
        }

        this.prevTime = time;
    }

    click(event) {
        this.lock();
    }

    onKeyDown(event) {
        switch(event.code) {
            case "ArrowUp":
            case "KeyW":
                this.doMoveForward = true;
                break;
            case "ArrowLeft":
            case "KeyA":
                this.doMoveLeft = true;
                break;
            case "ArrowDown":
            case "KeyS":
                this.doMoveBackward = true;
                break;
            case "ArrowRight":
            case "KeyD":
                this.doMoveRight = true;
                break;
            case "Space":
                this.doMoveUp = true;
                break;
            case "ShiftLeft":
                this.doMoveDown = true;
                break;
        }
    }

    onKeyUp(event) {
        switch(event.code) {
            case "ArrowUp":
            case "KeyW":
                this.doMoveForward = false;
                break;
            case "ArrowLeft":
            case "KeyA":
                this.doMoveLeft = false;
                break;
            case "ArrowDown":
            case "KeyS":
                this.doMoveBackward = false;
                break;
            case "ArrowRight":
            case "KeyD":
                this.doMoveRight = false;
                break;
            case "Space":
                this.doMoveUp = false;
                break;
            case "ShiftLeft":
                this.doMoveDown = false;
                break;
        }
    }

    wheel(event) {
        this.speed += event.deltaY * -1;
        if (this.speed < this.minSpeed) {
            this.speed = this.minSpeed;
        }
    }
}

export { FlyControlsX };
