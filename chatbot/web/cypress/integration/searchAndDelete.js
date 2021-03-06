// A two second wait time to make sure everything is loaded
const waitTime = 2000;


// This test will search for a site, select the first document, and
// delete the last entries
describe('Test search and deleting text and keyword', () => {
  beforeEach(() => {
    cy.visit('http://localhost:3000/')
      .wait(waitTime);
  });

  it('Search and delete answere and keyword for the first result ', () => {
    const url = 'https://www.trondheim.kommune.no/tema/kultur-og-fritid/lokaler/husebybadet/'
    // Type the url in the search bar
    cy.get('.searchInputField').children().get('input')
      .type(url)
      .should('have.value', url)
      .type('{enter}')
      .wait(waitTime);

    const title = 'e3878fe650dc125c5c70ada53cf266b93b4af782-4'
    // Get the first result after searching and check text is what we expect
    cy.get('.itemList').first().get('tr>td').eq(1)
      .invoke('text').then((text => {
        expect(text).to.eq(title)
      }));

    // click the first result
    cy.get('.itemList').first().get('tr>td').first().children().last()
      .click()
      .wait(waitTime);

    // Delete the manual entry
    // No errors should occur
    cy.get('.deleteManual')
      .click()
  });
}); 