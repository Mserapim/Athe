
Ext._define('judicial.PartLawsuitHandLess', {
    mixins: {
        '1': 'judicial.PartLawsuitMixin'
    },

    rest: 'judicial.PartLawsuitRestful',

    actionTitle: 'undefined',

    createLoadMask: function() {
      return new Ext.LoadMask(
        Ext.getBody(),
        {
          msg: 'registrando ação...'
        }
      );
    },

    on: function() {
        console.log('this is only fallback');
    },

    signFailureCallback: function(message) {
        Ext.Msg.show({
            title: 'Registrado ação',
            icon: Ext.Msg.INFO,
            buttons: Ext.Msg.OK,
            msg: message
        });

        this.factoryRestful().remove(this.oId,{}, false);
    },

    signSuccessCallback: function() {
        Ext.Msg.show({
            title: 'Registrado ação',
            icon: Ext.Msg.INFO,
            buttons: Ext.Msg.OK,
            msg: 'Ação "' + this.actionTitle + '" registrada com sucesso.'
        });

        this.close();
        core.invokeCallback((this.callback || {}).success);
    },

    factoryRestful: function(cfg) {

        if(!this._restful)
        {
            cfg = cfg || {};
            this._restful = Ext._create(this.rest, cfg);
        }

        return this._restful;
    },

    save: function(close) {
        var rest = this.factoryRestful();
        var cfg = {
            params: this.getParams(),
            externalCallback: this.callback
        };

        if(this.action === 'create')
            rest.create(
                cfg,
                {
                    el: Ext.getBody(),
                    waitMessage: 'Persistindo os dados.'
                }
            );
        else if(this.action === 'update')
            rest.update(
                this.oId,
                cfg,
                {
                    el: Ext.getBody(),
                    waitMessage: 'Persistindo os dados.'
                }
            );
    },

    close: function() {
        console.log('its is handless');
    },

    show: function() {
        if(this.action === 'create')
            Ext.Msg.show({
                title: 'Registrando ' + this.actionTitle,
                msg: 'Tem certeza que deseja registrar "' +  this.actionTitle +'""?',
                scope: this,
                icon: Ext.Msg.QUESTION,
                buttons: Ext.Msg.YESNO,
                fn: function(btn) {
                    if(btn === 'no') return;
                    this.sign();
                }
            });
        else
            Ext.Msg.show({
                title: 'Registrando ' + this.actionTitle,
                msg: this.actionTitle +', não permite edição.',
                icon: Ext.Msg.ERROR,
                buttons: Ext.Msg.OK
            });
    },

    sign: function() {
        var originalCallback = this.callback;

        this.callback = {
            success: {
                scope: this,
                fn: function(instance) {
                    var me = this;

                    me.oId = instance.pk;
                    this.callback = originalCallback;
                    setTimeout(
                        function() { me._sign(); },
                        50
                    );
                }
            }
        };

        this.save(true);
    },

    getParams: function() {
        return this.params;
    },

    constructor: function(cfg) {
        core.nullValue(cfg, {});

        console.log(cfg);

        this.params = (cfg.params || {});
        this.callback = (cfg.callback || {});
        this.action = (cfg.action || 'create');
        this.oId = (cfg.oId || undefined);

        judicial.PartLawsuitHandLess.superclass.constructor.call(this, cfg);
    }
});
