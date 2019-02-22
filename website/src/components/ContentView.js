import React from "react"

export default class ContentView extends React.Component {
	constructor() {
		super();
		this.state = {
			inputValue: "hardcoded text"
		}
	}

	componentDidMount() {
		// Fetch content
	}

	handleSubmit = (e) => {
		// Save data and delete entry in manual collection if needed
		e.preventDefault();
	}

	render() {

		return (
			<div>
				<h1>Content</h1>
				<form onSubmit={(e) => this.handleSubmit(e)}>
					<label>
						Text:
						<input type="text" name="text"
							value={this.state.inputValue}
							onChange={(e) => { this.setState({ inputValue: e.target.value }) }}
						/>
					</label>
					<br />
					<input type="submit" value="Save" />
				</form>
			</div >
		);

	}
}