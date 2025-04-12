Ext._define('rh.dayoff.mpmt.activity.SpecializedWindow', {
    extend: 'rh.dayoff.mpmt.activity.Window',

    width: 600,

    getWindowConfig: function (cfg) {
        if (cfg.actionCustom == 'suspend') 
            return this.getSuspension(cfg)
        else
            return this.getFieldsConfig(cfg)
    },

    getFieldsConfig:function(cfg){
        
        if (cfg.actionCustom == 'book_sell'){
            return [
                this.getInformation(cfg),
                this.getNewBookField(cfg),
                this.getNewBookSaleField(cfg),
                this.getNewBook(cfg),
            ]
        }else if (cfg.actionCustom == 'correct') {
            var sell = cfg.data[0].start_date?false:true
            if (sell){
                return [
                    this.getInformation(cfg),
                    this.getBookedUsufructsFieldSet(cfg),
                    this.getNewBookSaleField(cfg),
                    this.getNewBook(cfg),
                ]
            }else{
                return [
                    this.getInformation(cfg),
                    this.getBookedUsufructsFieldSet(cfg),
                    this.getNewBookField(cfg),
                    this.getNewBook(cfg),
                ]
            }
            
        }else if(cfg.actionCustom == 'remaining'){
            return [
                this.getInformation(cfg),
                this.getBookedUsufructsFieldSet(cfg),
                this.getNewBookField(cfg),
                this.getNewBook(cfg),
            ]
        }
        else {
            return [
                this.getInformation(cfg),
                this.getBookedUsufructsFieldSet(cfg),
                this.getNewBookField(cfg),
                this.getNewBookSaleField(cfg),
                this.getNewBook(cfg),
            ]
        }
    },

    // getManagerPanel: function (cfg) {
    //     if (!this._managementPanel)
    //         this._managementPanel = Ext._create('Ext.Panel', {
    //             frame: true,
    //             border: false,
    //             title: 'Marcação',
    //             layout: 'form',
    //             items: [
    //                 this.getFieldsConfig(cfg)
    //             ]
    //         });

    //     return this._managementPanel;
    // },

    getFormPanel: function (cfg) {
        if (!this._formPanel)
            this._formPanel = Ext._create('Ext.form.FormPanel', {
                border: false,
                frame: true,
                items: this.getWindowConfig(cfg)
                //items:this.getTabPanel(cfg)
            });

        return this._formPanel;
    },

    // getTabPanel: function (cfg) {
    //     if (!this._tabPanel)
    //         this._tabPanel = Ext._create('Ext.TabPanel', {
    //             height:cfg.actionCustom == 'book_sell'?500:700,
    //             border: false,
    //             activeTab: 0,
    //             deferredRender: false,
    //             items: [this.getManagerPanel(cfg)]
    //         });

    //     return this._tabPanel;
    // },
});
