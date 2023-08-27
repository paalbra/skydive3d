import * as THREE from 'three';
import { FlyControlsX } from './FlyControlsX.js';
import Stats from 'three/libs/stats.module.js';

let camera;
let controls;
let renderer;
let scene;
let stats;

const COLORS = [
    0xaa0000,
    0x00aa00,
    0x0000aa,
    0xaaaa00,
    0xaa00aa,
    0x00aaaa
];

function init() {
    scene = new THREE.Scene();

    var canvas = document.createElement("canvas");
    var context = canvas.getContext("webgl2", {alpha: false});
    renderer = new THREE.WebGLRenderer({canvas: canvas, context: context});
    renderer.setClearColor(0xcccccc);
    renderer.setSize(window.innerWidth, window.innerHeight);

    document.body.appendChild(renderer.domElement);

    camera = new THREE.PerspectiveCamera(80, window.innerWidth / window.innerHeight, 10, 20000);
    controls = new FlyControlsX(camera, renderer.domElement);
    camera.position.set(7000, 7000, 7000);
    camera.lookAt(0, 0, 0);

    var grid = new THREE.GridHelper(20000, 20, 0xff0000, 0x666666);
    scene.add(grid);

    var axes = new THREE.AxesHelper(1000);
    scene.add(axes);

    var ambient_light = new THREE.AmbientLight(0xffffff, 0.2);
    scene.add(ambient_light);

    var directional_light = new THREE.DirectionalLight(0xffffff, 1);
    directional_light.position.set(1000, 10000, 1000);
    directional_light.castShadow = true;
    scene.add(directional_light);

    scene.fog = new THREE.Fog(0xcccccc, 10000, 20000);

    stats = new Stats();
    stats.showPanel(0);
    document.body.appendChild(stats.dom);

    var loader = new THREE.TextureLoader();
    loader.load("merged.png", function ( texture ) {
      var geometry = new THREE.PlaneGeometry(width, height, width/100, height/100);
      var material = new THREE.MeshBasicMaterial({map: texture, side: THREE.DoubleSide});
      var mesh = new THREE.Mesh(geometry, material);
      mesh.rotation.x = -(Math.PI / 2);
      mesh.position.set(width/2, 0, height/2);
      scene.add(mesh);
    });

    for (var index in series) {
        let color = COLORS[index] || getRandomColor();
        addSeries(series[index], color, 8, 0.9, false);
    }

    drawThing(0, 1000, 0, getRandomColor(), 200);

    window.addEventListener("resize", () => {
        camera.aspect = window.innerWidth/window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}

function addSeries(path, color, radius, opacity, closed) {
    var points = []
    for (var index in path) {
        var element = path[index];
        var easting = element["x"];
        var ele = element["ele"];
        var northing = element["z"];
        points.push(new THREE.Vector3(easting, ele, northing));
    }
    var curve = new THREE.CatmullRomCurve3(points);
    var tubularSegments = points.length;
    var radialSegments = 4;
    var geometry = new THREE.TubeGeometry(curve, tubularSegments, radius, radialSegments, closed);
    var material = new THREE.MeshBasicMaterial({color: color, transparent: true, opacity: opacity, wireframe: false});
    var curveObject = new THREE.Mesh(geometry, material);
    scene.add(curveObject);
}

function getRandomColor() {
    return Math.floor(Math.random()*0xffffff);
}

function drawThing(x, y, z, color, size) {
    var geometry = new THREE.SphereGeometry(size);
    var material = new THREE.MeshLambertMaterial({ color: color, transparent: true, opacity: 0.7});
    var cube = new THREE.Mesh(geometry, material);
    cube.position.set(x, y, z);
    scene.add(cube);
}

function animate() {
    stats.begin();

    controls.update();
    renderer.render(scene, camera);

    stats.end();

    requestAnimationFrame(animate);
}

init();
animate();
