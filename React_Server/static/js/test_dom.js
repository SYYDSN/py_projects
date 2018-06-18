const element = <h1>Hello, world</h1>;
ReactDOM.render(
  element,
  document.getElementById('example2')
);
function clock(){
    const element = (
        <div>
        <h3>{new Date().toLocaleString()}</h3>
        </div>
    );
    ReactDOM.render(
        element,
        document.getElementById("clock")
    );
}
setInterval(clock, 1000);

function Welcome(props){
    return <h4  className="aa">Hello, {props.name}</h4>;
}
const welcome_item = <Welcome name="my_name"/>;
ReactDOM.render(welcome_item, document.getElementById("welcome"));

function App(){
    return (
        <div>
            <Welcome name="jack" />
            <Welcome name="tom" />
        </div>
    );
}
ReactDOM.render(
    <App />,
    document.getElementById("app1")
);