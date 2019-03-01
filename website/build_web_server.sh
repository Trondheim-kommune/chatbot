npm install
cd ..
source venv/bin/activate
cd website/
npm run build
rm /var/www/html/ -r
cp build /var/www/html/ -r
