
import requests

def fetch_url(env, url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.ConnectionError as e:
        print(f"\nConnection error for {env} : {url} \nError: {str(e)}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"\nRequest error for {env} : {url} \nError: {str(e)}")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"\nHTTP error for {env} : {url} \nError: {str(e)}")
        return None
    except requests.RequestException as e:
        print(f"\nUnexpected error occoured for {env} : {url} \nError: {str(e)}")
        return None


def main(): 
    urls =  {
    'SIT-PC':'https://hvcp-sit-pc.int.b4cmr1.dlgmalz.co.uk/pc',
    'SIT-CC':'https://hvcp-sit-cc.int.b4cmr1.dlgmalz.co.uk/cc',
    'SIT-CMCC':'https://hvcp-sit-cccm.int.b4cmr1.dlgmalz.co.uk/ab/ContactManager.do',
    'NFT-PC':'https://hvcp-nft-pc.int.hvcptest.dlgmalz.co.uk/pc/PolicyCenter.do',
    'NFT-CC':'https://hvcp-nft-cc.int.hvcptest.dlgmalz.co.uk/cc/ClaimCenter.do',
    'NFT-CMCC':'https://hvcp-nft-cccm.int.hvcptest.dlgmalz.co.uk/ab/ContactManager.do',
    'E2ETT-PC':'https://hvcp-e2ett-pc.int.b4cmr1.dlgmalz.co.uk/pc/PolicyCenter.do',
    'E2ETT-CC':'https://hvcp-e2ett-cc.int.b4cmr1.dlgmalz.co.uk/cc/ClaimCenter.do',
    'E2ETT-CCCM':'https://hvcp-e2ett-cccm.int.b4cmr1.dlgmalz.co.uk/ab/ContactManager.do',
    'E2E-PC':'https://hvcp-e2e-pc.int.b4cmr1.dlgmalz.co.uk/pc/PolicyCenter.do',
    'E2E-CC':'https://hvcp-e2e-cc.int.b4cmr1.dlgmalz.co.uk/cc/ClaimCenter.do',
    'E2E-CCCM':'https://hvcp-e2e-cccm.int.b4cmr1.dlgmalz.co.uk/ab/ContactManager.do',
    'UAT-PC':'https://hvcp-uat-pc.int.b4cmr1.dlgmalz.co.uk/pc',
    'UAT-CC':'https://hvcp-uat-cc.int.b4cmr1.dlgmalz.co.uk/cc',
    'UAT-CCCM':'https://hvcp-uat-cccm.int.b4cmr1.dlgmalz.co.uk/ab/ContactManager.do',
    'UATTT-PC':'https://hvcp-uattt-pc.int.b4cmr1.dlgmalz.co.uk/pc',
    'UATTT-CC':'https://hvcp-uattt-cc.int.b4cmr1.dlgmalz.co.uk/cc',
    'UATTT-CCCM':'https://hvcp-uattt-cmcc.int.b4cmr1.dlgmalz.co.uk/ab/ContactManager.do'
    }

    succ_counter = 0
    error_counter = 0

    for env, url in urls.items():
        response_text = fetch_url(env, url)
        if response_text:
            succ_counter = succ_counter +1
        else:
            error_counter = error_counter + 1

    print(f"\nHealth Check Summary:\n Total URLs: {len(urls)}\n Successful: {succ_counter}\n Failed: {error_counter}")


if __name__== '__main__':
    main()