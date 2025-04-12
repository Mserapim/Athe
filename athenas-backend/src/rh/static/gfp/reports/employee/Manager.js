Ext._define('rh.gfp.reports.employee.Manager', {
    extend: 'toolkit.widget.TabPanel',

    BACKGROUND_COLOR: '#005a7d',
    CARD_HEIGHT: 200,             // card default height
    GAP: 7,                       // gap between panels

    _getSeparator: function () {
        return {
            height: this.CARD_HEIGHT,
            width: this.GAP,
            padding: 0,
            baseCls: '',
        };
    },

    _getDefaults: function () {
        return {
            flex: 1,
            height: this.CARD_HEIGHT,
            baseCls: 'x-river-panel',
            padding: this.GAP,
        };
    },

    getRowOne: function (cfg) {
        if (this._rowOne) {
            return this._rowOne;
        }

        this._rowOne = Ext._create('Ext.Panel', {
            border: false,
            bodyStyle: `background-color: ${this.BACKGROUND_COLOR}`,
            layout: {
                type: 'hbox',
                padding: `${this.GAP} ${this.GAP} 0 ${this.GAP}`,
            },
            defaults: this._getDefaults(),
            items: [
                {
                    title: 'Contracheque',
                    items: Ext._create('rh.gfp.reports.employee.forms.PayCheck'),
                },
                this._getSeparator(),
                {
                    title: 'Ficha financeira',
                    items: Ext._create('rh.gfp.reports.employee.forms.FinancialStatement'),
                },
                this._getSeparator(),
                {
                    title: 'Ficha funcional',
                    items: Ext._create('rh.gfp.reports.employee.forms.EmployeeRecord'),
                },
            ],
        });

        return this._rowOne;
    },

    getRowTwo: function (cfg) {
        if (this._rowTwo) {
            return this._rowTwo;
        }

        this._rowTwo = Ext._create('Ext.Panel', {
            border: false,
            bodyStyle: `background-color: ${this.BACKGROUND_COLOR}`,
            layout: {
                type: 'hbox',
                padding: `${this.GAP} ${this.GAP} 0 ${this.GAP}`,
            },
            defaults: this._getDefaults(),
            items: [
                {
                    title: 'Comprovante de rendimentos',
                    items: Ext._create('rh.gfp.reports.employee.forms.ComprovanteRendimentos'),
                },
                this._getSeparator(),
                {
                    title: 'Requerimentos',
                    items: Ext._create('rh.gfp.reports.employee.forms.Documents'),
                },
                this._getSeparator(),
                {
                    title: 'Outros requerimentos',
                    items: Ext._create('rh.gfp.reports.employee.forms.StaticDocuments'),
                },
            ],
        });

        return this._rowTwo;
    },

    getRowThree: function (cfg) {
        if (this._rowThree) {
            return this._rowThree;
        }

        this._rowThree = Ext._create('Ext.Panel', {
            border: false,
            bodyStyle: `background-color: ${this.BACKGROUND_COLOR}`,
            layout: {
                type: 'hbox',
                padding: `${this.GAP} ${this.GAP} ${this.GAP} ${this.GAP}`,
            },
            defaults: this._getDefaults(),
            items: [
                {
                    title: 'Folha de ponto',
                    items: Ext._create('rh.gfp.reports.employee.forms.TimeSheet'),
                },
                this._getSeparator(),
                {
                    baseCls: '',
                },
                this._getSeparator(),
                {
                    baseCls: '',
                },
            ],
        });

        return this._rowThree;
    },

    getMainContainer: function (cfg) {
        if (this._mainContainer) {
            return this._mainContainer;
        }

        this._mainContainer = Ext._create('Ext.Panel', {
            layout: 'form',
            border: false,
            autoScroll: true,
            bodyStyle: `background-color: ${this.BACKGROUND_COLOR}`,
            items: [
                this.getRowOne(cfg),
                this.getRowTwo(cfg),
                this.getRowThree(cfg),
            ],
        });

        return this._mainContainer;
    },

    constructor: function (cfg) {
        cfg = cfg || {};

        Ext.applyIf(cfg, {
            title: 'Relatórios',
        });

        Ext.apply(cfg, {
            layout: 'fit',
            items: this.getMainContainer(cfg),
        });

        rh.gfp
          .reports
          .employee
          .Manager
          .superclass
          .constructor
          .call(this, cfg);
    },
});
