export function textoNormalMobile(textoNormal: string, textoMobile: string) :string {
    let isMobile = window.innerWidth <= 768;

    if (isMobile) {
        return textoMobile;
    }

    return textoNormal;
}
