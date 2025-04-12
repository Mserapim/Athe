/**
 *
 **/
Ext._define('core.TilePagePanel', {
    extend: 'Ext.Container',

    extraClasses: [],

    mainExtraClasses: [],

    getPageContainer: function() {
        if(!this._pageContainer)
            this._pageContainer = Ext._create('Ext.Container', {
                autoEl: 'div',
                cls: ['papper-model'].concat(this.extraClasses || [])
            });

        return this._pageContainer;
    },

    setPageContent: function(content) {
        var container = this.getPageContainer();

        container.removeAll();
        container.add(
            Ext._create('Ext.Container', {
                autoEl: 'div',
                style: {
                    margin: '15mm 20mm'
                },
                html: content
            })
        );

        this.extraContainer.forEach(
            function(container) {
                this.remove(container);
            },
            this
        );

        this.extraContainer = [];
        this.doLayout(false, true);
    },

    addPageContent: function(content) {
        var container = Ext._create('Ext.Container', {
            autoEl: 'div',
            cls: ['papper-model'].concat(this.extraClasses || [])
        });

        container.add(
            Ext._create('Ext.Container', {
                autoEl: 'div',
                style: {
                    margin: '15mm 20mm'
                },
                html: content
            })
        );

        this.add(container);
        this.doLayout();

        this.extraContainer.push(container);
    },

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.applyIf(
            cfg,
            {

            }
        );

        Ext.apply(
            cfg,
            {
                extraContainer: [],
                autoEl: 'div',
                cls: ['x-panel-body', 'papper-container-' + (cfg.papperModel || 'a4')].join(' ')
            }
        );

        // this.callParent([cfg]);
        core.TilePagePanel.superclass.constructor.call(this, cfg);

        this.add(this.getPageContainer());
    }
});
