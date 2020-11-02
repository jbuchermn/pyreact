import './App.css';

export default (props) => {
  return (
    <div className="App">
        <h1>{props.dummy ? props.dummy.counter : "WAITING"}</h1>
        <div style={{ backgroundColor: 'blue', width: 100, height: 100 }} onClick={() => props.dummy.inc()} />
    </div>
  );
}
