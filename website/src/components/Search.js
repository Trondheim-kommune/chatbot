import React from "react"

export default class Search extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      url: ''
    }
  }
  handleSubmit = (e) => {
    // Do something with the url
    e.preventDefault();
  }
  render() {
    return (
      <form onSubmit={(e) => this.handleSubmit(e)}>
        <label>
          URL:
            <input type="text" name="url"
            placeholder="https://www.trondheim.kommune.no/"
            leng
            onChange={e => this.setState({ url: e.target.value })} />
        </label>
        <input type="submit" value="Search" />
      </form>
    );

  }
}
