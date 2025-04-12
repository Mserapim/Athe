Ext._define('core.utils.LoadMaskMixin', {

    __loadMask: undefined,

    loadingMessage: 'Carregando dados...',

    getLoadMask: function () {
        if (this.__loadMask) {
            return this.__loadMask;
        }

        if (!this.getEl()) {
            return null;
        }

        this.__loadMask = new Ext.LoadMask(this.getEl(), {
            msg: this.loadingMessage
        });

        return this.__loadMask;
    },

    setLoadMaskTarget: function (target) {
        this.__loadMask = new Ext.LoadMask(target, {
            msg: this.loadingMessage
        });
    },

    showMask: function () {
        this.getLoadMask() && this.getLoadMask().show();
    },

    hideMask: function () {
        this.getLoadMask() && this.getLoadMask().hide();
    },
});
