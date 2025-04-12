Ext._define('rh.person.merge.NaturalPersonDataPanel', {
    extend: 'Ext.form.FormPanel',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});
        var owner = this;
        Ext.apply(
            cfg,
            {
                id: 'naturalpersondata',
                items: this.getDisplayDiff({}),
                listeners: {
                    scope: this,
                    afterrender: function() {},
                    afterlayout: function() {},
                    activate: function() {
                        this.getPersonDiff();
                    },
                    show: function() {},
                    destroy: function() {},
                }
            }
        );
        rh.person.merge.NaturalPersonDataPanel.superclass.constructor.call(this, cfg);
    },

    getDisplayDiff: function(){
        return [];
    },

    getPersonDiff: function(){
        var rest = Ext._create('rh.person.naturalperson.Grid', {}).factoryRestful();
        var mask = Ext._create('Ext.LoadMask', this.getEl(), {msg: 'Lendo dados...'});
        var params = {pkset:[]};
        this.person.forEach(function(item){ params.pkset.push(item.pk);});

        mask.show();

        rest.getPersonDiff(
            params,
            {
                scope: this,
                fn: function(rst) {
                    this._process(rst);
                }
            },
            {
                scope: this,
                fn: function(message) {
                    this.responseMessage(Ext.Msg.ERROR, message);
                }
            },
            {
                scope: this,
                fn: function() {
                    mask.hide();
                }
            }
        );
    },

    responseMessage: function(icon, message) {
        Ext.Msg.show({
            title: 'Mesclar pessoas',
            buttons: Ext.Msg.OK,
            icon: icon,
            msg: message
        });
    },

    _process: function(rst){
        var scope = this;
        rst.result.forEach(function(item){
            if(item.fieldSet == false){
                var item = Ext._create('rh.person.merge.GenericFieldSet', {field: item});
                scope.add(item);
            }else if(item.grid == true){
                scope.windowCt.addRoute(item.items);
            }else{
                if(item.availableMerge == false)
                    Ext.Msg.show({
                        title: 'Erro',
                        msg: item.message,
                        buttons: Ext.Msg.OK,
                        icon: Ext.Msg.ERROR,
                    });
            }
        });
        this.doLayout();
    },

    getFormValuesChecked: function(){
        var chosen = {};
        var items = this.getForm().items;
        this._chooseChecked().forEach(function(item){
            items.items.forEach(function(it){
                if(it.name == item.field_name){
                    chosen[item.field_name.split('_')[0]] = it.valueRaw;
                }
            });
        });
        return chosen;
    },

    _chooseChecked: function(){
        var checkeds = [];
        this.getForm().items.items.forEach(function(item){
            if(item.name.indexOf('check') != -1 && item.getValue() == true)
                checkeds.push(item);
        });
        return checkeds;
    },
});
