import React from 'react';
import { fetchData } from '../utils/Util';
import css from './DocumentView.module.css';
import { withToastManager } from 'react-toast-notifications';
import { Typography, Input, Button } from 'antd';
import classNames from 'classnames';

const { Title, Paragraph } = Typography;
const { TextArea } = Input;

/* 
This component displays the content field in a document from the manual collection
and the corresponding document in the prod collection.
You can edit the "texts" field and the "keywords" field manually.
 */
class DocumentView extends React.Component {
  state = {
    keywordError: false,
    manual: null,
    automatic: null,
    title: null,
    url: null,
  }

  async componentDidMount() {
    // Fetch content.
    const content = await fetchData(
      process.env.REACT_APP_SERVER_URL + 'v2/content/' + this.props.id + '/',
      'GET',
    );

    this.setState({
      manual: content.manual.id ? content.manual : content.prod,
      automatic: content.prod,
      title: content.prod.title,
      url: content.url,
    });
  }

  validateKeywords = () => this.state.manual.content.keywords.every(entry =>
    !/\s/g.test(entry['keyword']));


  handleSubmit = async e => {
    e.preventDefault();

    if (!this.validateKeywords()) {
      this.setState({
        keywordError: true,
      });

      return;
    }

    this.setState({
      keywordError: false,
    });

    // Save data and delete entry in manual collection if needed.
    const data = { id: this.props.id, content: this.state.manual.content };

    await fetchData(
      process.env.REACT_APP_SERVER_URL + 'v2/content/' + this.props.id + '/',
      'PUT',
      data,
    );

    this.props.toastManager.add('Lagringen av manuelle endringer var vellykket.', {
      appearance: 'success',
      autoDismiss: true,
    });
  };

  createNewAnswer = e => {
    e.preventDefault();
    if (this.state.manual) {
      this.setState(prevState => ({
        manual: {
		  content: {
            ...prevState.manual.content,
            texts: [...prevState.manual.content.texts, ''],
		  }
        },
      }));
    }
  };

  createNewKeyword = e => {
    e.preventDefault();
    if (this.state.manual) {
      this.setState(prevState => ({
        manual: {
		  content: {
			...prevState.manual.content,
			keywords: [
			  ...prevState.manual.content.keywords,
			  { keyword: '', confidence: 1 },
		 	],
		  }
        },
      }));
    }
  };

  deleteKeyword = (e, i) => {
    e.preventDefault();
    this.setState(prevState => ({
      manual: {
		content: {
		  ...prevState.manual.content,
		  keywords: [
		    ...prevState.manual.content.keywords.slice(0, i),
			...prevState.manual.content.keywords.slice(i + 1),
		  ],
		}
      },
    }));
  };

  deleteAnswer = (e, i) => {
    e.preventDefault();
    this.setState(prevState => ({
      manual: {
        content: {
            ...prevState.manual.content,
            texts: [
              ...prevState.manual.content.texts.slice(0, i),
              ...prevState.manual.content.texts.slice(i + 1),
            ],
        }
      },
    }));
  };

  deleteDocument = (e, i) => {
    e.preventDefault();
    fetchData(
      process.env.REACT_APP_SERVER_URL + 'v2/content/' + this.props.id + '/',
      'DELETE'
    ).then(() => {
      this.props.changeView('main');
    });
  }

  render() {
    let textAreasManual;
    if (this.state.manual) {
      /* map through the texts field from manual */
      textAreasManual = this.state.manual.content.texts.map((text, i) => (
        <div key={i} className="answers">
          <div className="answer">
            <TextArea
              rows="10"
              cols="50"
              value={text}
              className={css.answer}
              onChange={e => {
                const value = e.target.value;

                this.setState(prevState => ({
                  manual: {
                    content: {
                      ...prevState.manual.content,
                      texts: [
                        ...prevState.manual.content.texts.slice(0, i),
                        value,
                        ...prevState.manual.content.texts.slice(i + 1),
                      ],
                    }
                  },
                }));
              }}
            />
          </div>

          <Button type="danger" onClick={e => this.deleteAnswer(e, i)}>
            Slett svar
          </Button>
        </div>
      ));
    }

    let keywordsManual;
    if (this.state.manual) {
      /* Map through the keywords from manual */
      keywordsManual = this.state.manual.content.keywords.map((keyword, i) => (
        <div key={i} className={css.keywordListItem}>
          <Input
            type="text"
            value={keyword['keyword']}
            className={classNames(css.keywordInput, 'keywordManual')}
            onChange={e => {
              e.preventDefault();
              const value = e.target.value;
              this.setState(prevState => ({
                manual: {
                  content: {
                    ...prevState.manual.content,
                    keywords: [
                      ...prevState.manual.content.keywords.slice(0, i),
                      {
                         keyword: value,
                         confidence: prevState.manual.content.keywords[i].confidence,
                      },
                      ...prevState.manual.content.keywords.slice(i + 1),
                    ],
                  }
                },
              }));
            }}
          />

          <Input
            className={css.confidenceInput}
            type="number"
            min="0"
            max="1"
            step="0.000000000000000001"
            value={keyword['confidence']}
            onChange={e => {
              e.preventDefault();
              const value = parseFloat(e.target.value);
              this.setState(prevState => ({
                manual: {
                  content: {
                    ...prevState.manual.content,
                    keywords: [
                      ...prevState.manual.content.keywords.slice(0, i),
                      {
                        keyword: prevState.manual.content.keywords[i].keyword,
                        confidence: value,
                      },
                      ...prevState.manual.content.keywords.slice(i + 1),
                    ],
                  }
                },
              }));
            }}
          />

          <Button
            type="danger"
            onClick={e => this.deleteKeyword(e, i)}
          >
            Slett nøkkelord
          </Button>
        </div>
      ));
    }

    let textAreasAutomatic;
    if (this.state.automatic) {
      /* Map through the texts field from prod */
      textAreasAutomatic = this.state.automatic.content.texts.map((text, i) => (
        <TextArea readOnly key={i} rows="10" cols="50" value={text} className={css.answer} />
      ));
    }

    let keywordsAutomatic;
    if (this.state.automatic) {
      /* Map through the keywords field from prod */
      keywordsAutomatic = this.state.automatic.content.keywords.map((keyword, i) => (
        <div key={i} className={css.keywordListItem}>
          <Input className={css.keywordInput} readOnly type="text" value={keyword['keyword']} />
          <Input className={css.confidenceInput} readOnly type="text" value={keyword['confidence']} />
        </div>
      ));
    }

    return (
      <div>
        {this.state.url && (
          <Title level={2}>
            <a href={this.state.url}>{this.state.title}</a>
          </Title>
        )}

        <div className="flex">
          {this.state.manual && (
            <div className="sub-container">
              <Title level={3}>Manuelle endringer</Title>

              <Paragraph>
                Her kan du endre svarene til botten manuelt. Oppdater teksten og
                trykk på lagre for å oppdatere.
              </Paragraph>

              <Title level={4}>Svar</Title>

              <form>
                {textAreasManual}

                <div>
                  <Button
                    type="primary"
                    className={classNames(css.addAnswer, 'newText')}
                    onClick={e => this.createNewAnswer(e)}
                  >
                    Nytt svar
                  </Button>
                </div>

                <Paragraph>
                  Man kan også oppdatere, legge til og slette nøkkelord og
                  selvsikkerheten deres.
                </Paragraph>

                <Paragraph>
                  Selvsikkerheten er et tall fra 0 til 1. 1  betyr at du må
                  ha dette søkeordet for å få dette svaret.
                </Paragraph>

                <Title level={4}>Nøkkelord</Title>

                {this.state.keywordError && (
                  <Paragraph className={css.error}>Nøkkelord kan ikke inneholde mellomrom.</Paragraph>
                )}

                {keywordsManual}

                <div className={css.buttonGroup}>
                  <Button type="primary"
                    className='save'
                    onClick={e => this.handleSubmit(e)}>Lagre</Button>
                  <Button type="secondary"
                    className='newKeyword'
                    onClick={e => this.createNewKeyword(e)}>Nytt nøkkelord</Button>
                  <Button type="danger"
                    className="deleteManual"
                    onClick={e => this.deleteDocument(e)}>Slett manuelle endringer</Button>
                </div>
              </form>
            </div>
          )}

          {this.state.automatic && (
            <div className="sub-container">
              {this.state.url && (
                <Title level={3}>
                  Automatisk hentet data
                </Title>
              )}

              <Paragraph>
                Sammenlign de manuelle endringene med informasjonen hentet fra
                nettsiden
              </Paragraph>

              <Title level={4}>Svar</Title>
              {textAreasAutomatic}

              <Title level={4} className={css.pushTop}>Nøkkelord</Title>
              {keywordsAutomatic}
            </div>
          )}
        </div>
      </div>
    );
  }
}

export default withToastManager(DocumentView);
