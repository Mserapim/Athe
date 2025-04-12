Ext._define('rh.person.merge.SendPanel', {
    extend: 'Ext.form.FormPanel',

    constructor: function(cfg) {
        cfg = core.nullValue(cfg, {});

        Ext.apply(
            cfg,
            {
                id: 'sendpanel',
                buttons: [
                    {
                        text: "Mesclar",
                        scope: this,
                        handler: function(){
                            this.mergeData();
                        },
                    }
                ],
            }
        );
        rh.person.merge.SendPanel.superclass.constructor.call(this, cfg);
    },

    mergeData: function(){
        var rest = Ext._create('rh.person.naturalperson.Grid', {}).factoryRestful();
        var mask = Ext._create('Ext.LoadMask', this.getEl(), {msg: 'Persistindo dados...'});
        var params = this.ownerCt._naturalPersonData.getFormValuesChecked();
        var pkset = [];
        this.person.forEach(function(item){ pkset.push(item.pk);});
        params['pkset'] = pkset;
        var length = Object.keys(params).length;
        this.windowCt.getGridArray().forEach(function(item){
            var values = [];
            item.getSelectionModel().getSelections().forEach(function(it){
                values.push(it.data.pk);
            });
            if(values.length > 0){
                params[length] = {'config': item.configOfTypeObj, 'values': values};
                length += 1;
            }
        });

        params = Ext.encode(params);

        mask.show();

        rest.mergeData(
            params,
            {
                scope: this,
                fn: function(rst) {
                    console.debug(rst);
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
                    this.ownerCt.ownerGrid.getStore().load();
                    this.ownerCt.close();
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

});
