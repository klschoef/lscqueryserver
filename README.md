# LSC Query Server

## Setup

## Documentation

### CLIP Server
The clip server will only be used for retrieved messages with the content type `textquery`, and only if the 

### Parse Parameters Regex
The used regex is `-([a-zA-Z]+)\s(\S+)`. This regex fetch the parameters from the message, and the parameters are in the form `-parameter value`. 
The parameter is a string that starts with a `-` and is followed by a space and the value. The value can be any string that does not contain a space.
Strings which are not in the form `-parameter value` will fetched for the textquery with clip, with the code `const updatedString = inputString.replace(regex, '').trim();`

### '<' parameter
The `<` parameter is used to specify which images or keyframes was shown before. Especially for video search it is useful, to find the correct keyframes.
Example Video: A car drives on a street, then we have a switch to a restaurant where a human eats something. The example query can be 'car street < restaurant human'.

In the case of lifelogs, we need to search in the same day, instead of the keyframes.